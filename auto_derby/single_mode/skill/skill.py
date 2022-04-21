# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Text, Tuple

import numpy as np

from ... import mathtools
from .globals import g

from auto_derby.constants import RuningStyle, RaceType, SkillStyle

class Skill:
    
    @staticmethod
    def new() -> Skill:
        return g.skill_class()

    def __init__(self) -> None:
        self.name = ""
        self.pick = 0
        self.running_type = 0
        self.distance_type = 0
        self.skill_type = 0
        
        self.price = 0

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Skill) and self._equal_key() == other._equal_key()

    def _equal_key(self):
        return (self.name)

    def __str__(self):
        return f"Skill<{self.name}>#{self.pick}"

    def __bool__(self) -> bool:
        return self.name != ""

    def to_dict(self) -> Dict[Text, Any]:
        d = {
            "name": self.name,
            "pick": self.pick,
            "running_type": self.running_type,
            "distance_type": self.distance_type,
            "skill_type": self.skill_type,
        }
        return d

    @classmethod
    def from_dict(cls, d: Dict[Text, Any]):
        v = cls.new()
        v.name = d["name"]
        v.pick = d["pick"]
        v.running_type = d["running_type"]
        v.distance_type = d["distance_type"]
        v.skill_type = d["skill_type"]
        return v
        
        
g.skill_class = Skill