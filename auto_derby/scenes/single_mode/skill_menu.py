# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
import os
import time
import numpy as np
from typing import Any, Dict, Iterator, Sequence, Text, Tuple

import cv2
from PIL.Image import Image

from ... import action, imagetools, mathtools, ocr, template, templates
from ...single_mode import Context, skill
from ...single_mode.skill import Skill
from ..scene import Scene, SceneHolder
from ..vertical_scroll import VerticalScroll
from .command import CommandScene

from auto_derby.constants import RuningStyle, SkillStyle

_LOGGER = logging.getLogger(__name__)

def _recognize_skill_remain_point(img: PIL.Image.Image) -> int:
    skill_remain_point_img = img.crop((414, 301, 465, 330))
    cv_img = imagetools.cv_image(skill_remain_point_img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
    text = ocr.text(imagetools.pil_image(binary_img))
    return int(text)


def _recognize_skill_point(img: PIL.Image.Image):
    cv_img = imagetools.cv_image(img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
    text = ocr.text(imagetools.pil_image(binary_img))
    return int(text)
    
 
def _is_learned_skill(img: PIL.Image.Image) -> bool:
    is_leaened = template.match(
        img, templates.SINGLE_MODE_LEARNED_SKILL
    )
    for _ in is_leaened:
        return True
    return False

def _title_image(rp: mathtools.ResizeProxy, title_img: Image) -> Image:
    cv_img = imagetools.cv_image(title_img.convert("L"))
    _, binary_img = cv2.threshold(cv_img, 120, 255, cv2.THRESH_BINARY_INV)
    binary_img = imagetools.auto_crop(binary_img)
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("title_img", imagetools.cv_image(title_img))
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    return imagetools.pil_image(binary_img)
    
def _recognize_item(rp: mathtools.ResizeProxy, img: Image) -> Skill:
    v = skill.from_name_image(_title_image(rp, img))
    return v

def _find_skill(img: PIL.Image.Image):
    rp = mathtools.ResizeProxy(img.width)

    min_y = rp.vector(130, 540)
    for _, pos in sorted(
        template.match(img, templates.SKILL_ITEM, templates.SKILL_ITEM_GOLD),
        key=lambda x: x[1][1],
    ):
        x, y = pos
        if y < min_y:
            # ignore partial visible
            continue
        bbox = (x - 400, y + 2, x - 130, y + 42)
        yield _recognize_item(rp, img.crop(bbox)), (x-5, y+40)
        
        
def _is_scroll_to_end(img: PIL.Image.Image) -> bool:
    is_end = template.match(
        img, templates.SKILL_SCROLL_TO_END, threshold=0.8
    )
    for _ in is_end:
        return True
    return False
    
def _pick_skill(img: PIL.Image.Image, ctx: Context, skill: Skill, pos, remain) -> bool:
    x, y = pos
    skill_point_img = img.crop((x - 68, y + 10, x - 25, y + 29))
    if _is_learned_skill(skill_point_img):
        return False
    point = _recognize_skill_point(skill_point_img)
    if point < remain:
        action.tap(pos)
        ctx.skills.append(skill)
        skill.price = point
        return True
    return False
    

class SkillMenuScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        rp = action.resize_proxy()
        self._scroll = VerticalScroll(
            origin=rp.vector2((15, 600), 540),
            page_size=150,
            max_page=25,
            max_change_direction = 0
        )

    @classmethod
    def name(cls):
        return "single-mode-skill-menu"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        CommandScene.enter(ctx)
        action.wait_tap_image(
            templates.SINGLE_MODE_SKILL_MENU_BUTTON,
        )
        action.wait_image_stable(templates.RETURN_BUTTON)
        return cls()
        
    def learn_skill(self, ctx: Context, blue_only=False) -> None:
        rp = action.resize_proxy()
        pick = False
        while self._scroll.next():
            img = template.screenshot()
            remain = _recognize_skill_remain_point(img)
            for skill, pos in _find_skill(img):
                if skill not in ctx.skills and (not blue_only or skill.skill_type == SkillStyle.BLUE.value):
                    if skill.pick == 3:
                        if _pick_skill(img, ctx, skill, pos, remain):
                            remain -= skill.price
                            pick = True
                            if skill.name == "余裕綽々":
                                ctx.long_distance_style = RuningStyle.HEAD
                    elif skill.pick == 2 and (not skill.running_type or skill.running_type == ctx.default_running_style.value):
                        if _pick_skill(img, ctx, skill, pos, remain):
                            remain -= skill.price
                            pick = True
                
            #if _is_scroll_to_end:
            #    break
        if pick:
            action.tap(rp.vector2((220, 680), 466))
            time.sleep(3.0)
            action.tap(rp.vector2((280, 780), 466))
            time.sleep(3.0)
            action.tap(rp.vector2((280, 780), 466))