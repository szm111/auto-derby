# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Text, Type

from ... import data

if TYPE_CHECKING:
    from .skill import Skill


class g:
    data_path: Text = data.path("single_mode_skills.jsonl")
    label_path: Text = ""
    skill_class: Type[Skill]
    name_label_similarity_threshold: Dict[int, float] = {}
    prompt_disabled = False
    explain_effect_summary = False
