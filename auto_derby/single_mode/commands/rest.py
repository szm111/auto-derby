# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from ... import action, templates
from ...scenes.single_mode.command import CommandScene
from .. import Context, Training
from .command import Command
from .globals import g


class RestCommand(Command):
    def execute(self, ctx: Context) -> None:
        g.on_command(ctx, self)
        CommandScene.enter(ctx)
        action.tap_image(
            templates.SINGLE_MODE_REST,
        )

    def score(self, ctx: Context) -> float:
        return g.rest_score(ctx)


def default_score(ctx: Context) -> float:
    t = Training.new()
    if ctx.turn_count_v2()>15:
        if ctx.is_ura:
            t.vitality = 30 / ctx.max_vitality
        else:
            t.vitality = 10 / ctx.max_vitality
    else:
        t.vitality = 50 / ctx.max_vitality
    return t.score(ctx)


g.rest_score = default_score
