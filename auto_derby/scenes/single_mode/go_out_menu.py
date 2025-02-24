# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
import os
from typing import Iterator, Text

import cv2
from PIL.Image import Image


from ... import action, imagetools, mathtools, ocr, template, templates, texttools, terminal
from ...single_mode import Context, go_out
from ..scene import Scene, SceneHolder

_LOGGER = logging.getLogger(__name__)


def _recognize_name(img: Image) -> Text:
    img = imagetools.resize(img, height=48)
    cv_img = imagetools.cv_image(img.convert("L"))
    _, binary_img = cv2.threshold(cv_img, 120, 255, cv2.THRESH_BINARY_INV)

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    text = ocr.text(imagetools.pil_image(binary_img))
    return texttools.choose(text, go_out.g.names, 0.3)


def _recognize_type(rp: mathtools.ResizeProxy, img: Image) -> int:
    friendship_gauge_pos = rp.vector2((330, 23), 500)
    has_friendship_gauge = (
        imagetools.compare_color(img.getpixel(friendship_gauge_pos), (236, 231, 228))
        > 0.9
    )
    if has_friendship_gauge:
        if len(go_out.g.names) > 1:
            return go_out.Option.TYPE_GROUP
        else:
            return go_out.Option.TYPE_SUPPORT
    return go_out.Option.TYPE_MAIN


def _recognize_item(rp: mathtools.ResizeProxy, img: Image) -> go_out.Option:
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("img", imagetools.cv_image(img))
        cv2.waitKey()
        cv2.destroyAllWindows()

    v = go_out.Option.new()
    rp = mathtools.ResizeProxy(img.width)
    v.type = _recognize_type(rp, img)
    if v.type != go_out.Option.TYPE_MAIN:
        event1_pos = rp.vector2((338 - 18, 353 - 286), 500)
        event2_pos = rp.vector2((375 - 18, 353 - 286), 500)
        event3_pos = rp.vector2((413 - 18, 353 - 286), 500)
        event4_pos = rp.vector2((450 - 18, 353 - 286), 500)
        event5_pos = rp.vector2((489 - 18, 353 - 286), 500)

        v.type = go_out.Option.TYPE_SUPPORT
        v.current_event_count = 0
        v.total_event_count = 5
        for pos in (
            event1_pos,
            event2_pos,
            event3_pos,
            event4_pos,
            event5_pos,
        ):
            is_gray = imagetools.compare_color(img.getpixel(pos), (231, 227, 225)) > 0.9
            if not is_gray:
                v.current_event_count += 1

        name_bbox = rp.vector4((95, 16, 316, 40), 540)
        v.name = _recognize_name(img.crop(name_bbox))
    return v
    
def _recognize_group_item(rp: mathtools.ResizeProxy, img: Image) -> go_out.Option:
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("img", imagetools.cv_image(img))
        cv2.waitKey()
        cv2.destroyAllWindows()

    v = go_out.Option.new()
    rp = mathtools.ResizeProxy(img.width)
    v.type = go_out.Option.TYPE_GROUP
    
    name_bbox = rp.vector4((95, 16, 316, 40), 540)
    v.name = _recognize_name(img.crop(name_bbox))
    
    event1_pos = rp.vector2((338 - 18, 353 - 286), 500)
    event2_pos = rp.vector2((375 - 18, 353 - 286), 500)

    v.current_event_count = 0
    
    if v.name != "玉座に集いし者たち":
        v.current_event_count = 0
        v.total_event_count = 1
        return v

    v.total_event_count = 2
    for pos in (
        event1_pos,
        event2_pos,
    ):
        is_gray = imagetools.compare_color(img.getpixel(pos), (231, 227, 225)) > 0.9
        if not is_gray:
            v.current_event_count += 1

    return v


def _recognize_menu(img: Image) -> Iterator[go_out.Option]:
    rp = mathtools.ResizeProxy(img.width)
    for _, pos in template.match(img, templates.SINGLE_MODE_GO_OUT_OPTION_LEFT_TOP):
        x, y = pos
        bbox = (
            x,
            y,
            x + rp.vector(500, 540),
            y + rp.vector(100, 540),
        )
        rp_type = mathtools.ResizeProxy(img.width)
        out_type = _recognize_type(rp_type, img.crop(bbox))
        
        croped_img = img.crop(bbox)
        rp_name = mathtools.ResizeProxy(croped_img.width)
        name_bbox = rp_name.vector4((95, 16, 316, 40), 540)
        name = _recognize_name(croped_img.crop(name_bbox))
        #terminal.pause(name)
        if name == "玉座に集いし者たち":
            action.tap((x + rp.vector(102, 540), y + rp.vector(46, 540)))
            img2 = template.screenshot()
            rp2 = mathtools.ResizeProxy(img2.width)
            for _, pos2 in template.match(img2, templates.SINGLE_MODE_GO_OUT_OPTION_LEFT_TOP):
                x2, y2 = pos2
                bbox2 = (
                    x2,
                    y2,
                    x2 + rp2.vector(500, 540),
                    y2 + rp2.vector(100, 540),
                )
                option = _recognize_group_item(rp2, img2.crop(bbox2))
                option.position_second = (x2 + rp2.vector(102, 540), y2 + rp2.vector(46, 540))
                option.position = (x + rp.vector(102, 540), y + rp.vector(46, 540))
                option.bbox = bbox
                yield option
            action.wait_tap_image(templates.CANCEL_BUTTON)
        else:
            option = _recognize_item(rp, img.crop(bbox))
            option.position = (x + rp.vector(102, 540), y + rp.vector(46, 540))
            option.bbox = bbox
            yield option


class GoOutMenuScene(Scene):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def name(cls):
        return "single-mode-go-out-menu"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        action.wait_image(templates.SINGLE_MODE_GO_OUT_MENU_TITLE)
        return cls()

    def recognize(self, ctx: Context) -> None:
        ctx.go_out_options = tuple(_recognize_menu(template.screenshot()))
        for option in ctx.go_out_options:
            print(option)
        #terminal.pause(f"find friend...............")
