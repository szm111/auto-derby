# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Iterator, Sequence, Tuple

from .effect_summary import EffectSummary
from ...constants import TrainingType

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..commands import Command
    from ..context import Context
    from .item import Item

    Plan = Tuple[float, Tuple[Item, ...]]
    
def _item_order(item: Item) -> int:
    es = item.effect_summary()
    if es.training_no_failure:
        return 100
    if es.vitality:
        return 100
    if es.training_effect_buff:
        return 200
    return 300


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
        item_summary = item.effect_summary()
        
        from ..commands import RaceCommand, TrainingCommand
        
        if isinstance(command, RaceCommand) and item.id not in [51, 52, 53]:
            continue
            
        if isinstance(command, TrainingCommand) and item.id in [51, 52, 53]:
            continue
            
        if isinstance(command, TrainingCommand) and item_summary.training_effect_buff and command.training.type not in item_summary.training_effect_buff.keys():
            continue
        
        for q_index in range(item.quantity):
            if (item_summary.vitality or item_summary.training_no_failure) and (es_after.vitality + ctx.vitality * 100 >= 50 or es_after.training_no_failure):
                break
            i = item.clone()
            i.quantity = 1
            s = round(i.effect_score(ctx, command, es_after), 2)
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
                if s_sub > s_best or (s_sub == s_best and sum(i.original_price for i in items_sub) < sum(j.original_price for j in items_best)):
                    s_best, items_best = s_sub, items_sub
            yield _with_log((s_best, items_best))
            if item_summary.training_effect_buff or item_summary.race_reward_buff:
                break
            if (item_summary.vitality or item_summary.training_no_failure) and (es_after.vitality + ctx.vitality * 100 >= 50 or es_after.training_no_failure) and item.id != 19:
                return

    return


def compute(
    ctx: Context,
    command: Command,
) -> Plan:
    return sorted(
        iterate(ctx, command, sorted(filter(lambda item: (item.id > 15 and item.id < 24) or item.id >42,tuple(ctx.items)), key=lambda x: (_item_order(x), -x.id)), EffectSummary()),
        key=lambda x: (round(-x[0]), sum(i.original_price for i in x[1])),
    )[0]