# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import io
import logging
from typing import Any, Text
from uuid import uuid4

from PIL.Image import Image

from auto_derby import mathtools, terminal, ocr


from ... import data, imagetools, web, texttools
from . import game_data
from .globals import g
from .skill import Skill

_LOGGER = logging.getLogger(__name__)


class _g:
    labels = imagetools.CSVImageHashMap(str)
    label_load_key: Any = None


def _load_key():
    return g.label_path


def reload():
    _g.labels.clear()
    _g.labels.load_once(data.path("single_mode_skill_labels.csv"))
    _g.labels.load_once(g.label_path)
    _g.labels.save_path = g.label_path
    _g.label_load_key = _load_key()


def reload_on_demand() -> None:
    if _g.label_load_key != _load_key():
        reload()


def _prompt(img: Image, h: Text, defaultValue: str, similarity) -> Skill:
    if g.prompt_disabled:
        ret = game_data.get(defaultValue)
        if similarity < 0.7:
            ret.pick = 0
        _LOGGER.warning("using low similarity skill: %s", ret)
        return ret
    close_img = imagetools.show(img)
    ans = ""
    try:
        y_or_n = ""
        while defaultValue and y_or_n not in ("Y", "N", "y", "n"):
            y_or_n = terminal.prompt(
                f"Matching current displaying image: value={defaultValue}, similarity={similarity:0.3f}.\n"
                "Is this correct? (Y/N)"
            )
        if y_or_n in ("Y" ,"y"):
            ans = defaultValue
        else:
            ans = terminal.prompt(
                "Corresponding text for current displaying image:")
    finally:
        close_img()
    _g.labels.label(h, ans)
    if ans not in game_data.names():
        game_data.update(ans)
    ret = game_data.get(ans)
    _LOGGER.info("labeled: hash=%s, value=%s", h, ret)
    return ret


def _default_name_label_similarity_threshold(skill: Skill) -> float:
    similarities_on_name = sorted(
        (
            (texttools.compare(i.name, skill.name), i)
            for i in game_data.iterate()
            if i.name != skill.name
        ),
        key=lambda x: -x[0],
    )
    if similarities_on_name:
        s, match = similarities_on_name[0]
    else:
        s, match = 0, None

    ret = mathtools.interpolate(
        int(s * 10000),
        (
            (0, 0.8),
            (7000, 0.8),
            (8000, 0.95),
            (10000, 1.0),
        ),
    )
    if ret > 0.8:
        _LOGGER.debug(
            "use higher name label similarity threshold %.2f for %s due to similar skill name: %s",
            ret,
            skill.name,
            match and match.name,
        )
    return ret


def _name_label_similarity_threshold(skill: Skill) -> float:
    if skill.name not in g.name_label_similarity_threshold:
        g.name_label_similarity_threshold[
            skill.name
        ] = _default_name_label_similarity_threshold(skill)
    return g.name_label_similarity_threshold[skill.name]


def from_name_image(img: Image) -> Item:
    reload_on_demand()
    h = imagetools.image_hash(img, divide_x=4)
    if _g.labels.is_empty():
        return _prompt(img, h, "",0)
    res = _g.labels.query(h)
    _LOGGER.debug("query label: %s by %s", res, h)
    skill = game_data.get(res.value)
    if skill and res.similarity > _name_label_similarity_threshold(skill):
        return skill
    #else:
        #cv_img = imagetools.cv_image(img.convert("L"))
        #cv_img = imagetools.level(
        #    cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
        #)
        #_, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
    #    text = ocr.text(img)
    #    if text in game_data.names():
    #        return game_data.get(text)
    return _prompt(img, h, skill.name if skill else 0,res.similarity)
