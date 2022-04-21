# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, Text

from .globals import g
from .skill import Skill


class _g:
    load_key: Any = None
    skill_data: Dict[str, Dict[Text, Any]] = {}


def _load_key():
    return g.data_path


def _iter(p: Text):
    with open(p, "r", encoding="utf-8") as f:
        for i in f:
            yield json.loads(i)
            
def _save(data) -> None:
    with open(g.data_path, "a", encoding="utf-8") as f:
        json.dump(data.to_dict(), f, ensure_ascii=False)
        f.write("\n")


def reload():
    _g.skill_data = {i["name"]: i for i in _iter(g.data_path)}
    _g.load_key = _load_key()


def reload_on_demand() -> None:
    if _g.load_key != _load_key():
        reload()
        
def update(name: str) -> None:
    reload_on_demand()
    v = Skill.new()
    v.name = name
    v.pick = 0
    v.running_type = 0
    v.distance_type = 0
    v.skill_type = 0
    _g.skill_data[name] = v.to_dict()
    _save(v)
        
        
def get(name: str) -> Skill:
    reload_on_demand()
    v = _g.skill_data.get(name)
    if v is None:
        v = Skill.new()
        v.name = name
        v.pick = 0
        v.running_type = 0
        v.distance_type = 0
        v.skill_type = 0
        return v
    return Skill.from_dict(v)


def iterate() -> Iterator[Skill]:
    reload_on_demand()
    for i in _g.skill_data.values():
        yield Skill.from_dict(i)
        
def names() -> Iterator[str]:
    reload_on_demand()
    for i in _g.skill_data.keys():
        yield i