# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Iterator, Sequence, Tuple

from .effect_summary import EffectSummary

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..commands import Command
    from ..context import Context
    from .item import Item

    Plan = Tuple[float, Tuple[Item, ...]]


def iterate(
    ctx: Context,
    command: Command,
    items: Sequence[Item],
    summary: EffectSummary,
) -> Iterator[Plan]:
    def _with_log(p: Plan):
        _LOGGER.debug("score: %.2f: %s", p[0], ",".join(i.name for i in p[1]))
        return p

    yield (0, ())
    for index, item in enumerate(items):
        s_current = 0
        items_current: Sequence[Item] = ()
        es_after = summary.clone()
        
        for q_index in range(item.quantity):
            if (item.effect_summary().vitality or item.effect_summary().training_no_failure) and (es_after.vitality + ctx.vitality * 100 >= 50 or es_after.training_no_failure):
                break
            i = item.clone()
            i.quantity = 1
            s = i.effect_score(ctx, command, es_after)
            if s <= 0:
                break
            s_e = i.expected_effect_score(ctx, command)
            if s <= s_e:
                break
            es_after.add(item)
            s_current += s
            items_current += (i,)

            s_best, items_best = (s_current, items_current)
            for sub_plan in iterate(ctx, command, items[index + 1 :], es_after,):
                s_sub, items_sub = (s_current + sub_plan[0], (*items_current, *sub_plan[1]))
                if round(s_sub) > round(s_best) or (round(s_sub) == round(s_best) and sum(i.original_price for i in items_sub) < sum(j.original_price for j in items_best)):
                    s_best, items_best = s_sub, items_sub
            yield _with_log((s_best, items_best))
            if item.effect_summary().training_effect_buff or item.effect_summary().race_reward_buff:
                break

    return


def compute(
    ctx: Context,
    command: Command,
) -> Plan:
    return sorted(
        iterate(ctx, command, tuple(ctx.items), EffectSummary()),
        key=lambda x: (round(-x[0]), sum(i.original_price for i in x[1])),
    )[0]