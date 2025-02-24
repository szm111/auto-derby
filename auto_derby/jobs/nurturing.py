# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import logging
import time
from auto_derby.single_mode.commands import RaceCommand, TrainingCommand
from typing import Callable, Iterator, List, Text, Tuple, Union

from .. import action, config, template, templates, terminal, scenes
from ..constants import RacePrediction
from ..scenes.single_mode import (
    AoharuBattleConfirmScene,
    AoharuCompetitorScene,
    AoharuMainScene,
    CommandScene,
    RaceMenuScene,
    SkillMenuScene,
    RaceTurnsIncorrect,
    ShopScene,
)
from ..scenes.single_mode.item_menu import ItemMenuScene
from ..single_mode import Context, commands, event, item

LOGGER = logging.getLogger(__name__)


ALL_OPTIONS = [
    templates.SINGLE_MODE_OPTION1,
    templates.SINGLE_MODE_OPTION2,
    templates.SINGLE_MODE_OPTION3,
    templates.SINGLE_MODE_OPTION4,
    templates.SINGLE_MODE_OPTION5,
]


def _handle_option():
    time.sleep(0.2)  # wait animation
    ans = event.get_choice(template.screenshot(max_age=0))
    action.tap_image(ALL_OPTIONS[ans - 1])


def _handle_shop(ctx: Context, cs: CommandScene):
    ctx.do_shopping = False
    if not (cs.has_shop and ctx.shop_coin):
        return
    scene = ShopScene.enter(ctx)
    scene.recognize(ctx)

    scores_of_items = sorted(
        (
            (i.exchange_score(ctx), i.expected_exchange_score(ctx), i)
            for i in scene.items
        ),
        key=lambda x: x[0] - x[1],
        reverse=True,
    )

    LOGGER.info("shop items")
    LOGGER.info(ctx.shop_coin)
    LOGGER.info(scores_of_items)
    cart_items: List[item.Item] = []
    total_price = 0
    for s, es, i in scores_of_items:
        status = ""
        if (
            sum(1 for j in cart_items if j.id == i.id) + ctx.items.get(i.id).quantity
            >= i.max_quantity
        ):
            status = "<max quantity>"
        elif total_price + i.price > ctx.shop_coin:
            status = "<coin not enough>"
        elif s > es:
            status = "<in cart>"
            cart_items.append(i)
            total_price += i.price
        LOGGER.info("score:\t%2.2f/%2.2f:\t%s\t%s", s, es, i, status)
    remain_size = scene.exchange_items(ctx, cart_items)
    if remain_size < len(cart_items):
        time.sleep(2.0)
        action.wait_tap_image(templates.SINGLE_MODE_CONFIRM_BUTTON)
        time.sleep(2.0)
        action.wait_tap_image(templates.CLOSE_BUTTON)

    cs.enter(ctx)
    if any(i.should_use_directly(ctx) for i in cart_items):
        _handle_item_list(ctx, cs)
        cs.recognize(ctx)
    return


def _handle_item_list(ctx: Context, cs: CommandScene):
    if not cs.has_shop:
        return
    if ctx.items_last_updated_turn == 0 or ctx.do_recognize:
        scene = ItemMenuScene.enter(ctx)
        scene.recognize(ctx)
        ctx.do_recognize = False
    items = tuple(i for i in ctx.items.full_list() if i.should_use_directly(ctx))
    if items:
        scene = ItemMenuScene.enter(ctx)
        scene.use_items(ctx, items)
    cs.enter(ctx)
    return
    
def _handle_skill(ctx: Context, cs: CommandScene, blue_onlye = False):
    scene = SkillMenuScene.enter(ctx)
    num = action.count_image(
            templates.SINGLE_MODE_RACE_START_BUTTON,
            templates.SINGLE_MODE_CONTINUOUS_RACE_TITLE,
            )
        
    while(num > 0):
        ctx.scene = scenes.UnknownScene()
        scene = CommandScene.enter(ctx)
        scene = SkillMenuScene.enter(ctx)
        num = action.count_image(
            templates.SINGLE_MODE_RACE_START_BUTTON,
            templates.SINGLE_MODE_CONTINUOUS_RACE_TITLE,
            )
    scene.learn_skill(ctx, blue_onlye)
    cs.enter(ctx)
    return
    

class ItemNotFound(ValueError):
    def __init__(self) -> None:
        super().__init__("Not found the item want to use")


class _CommandPlan:
    def __init__(
        self,
        ctx: Context,
        command: commands.Command,
    ) -> None:
        self.command = command
        self.command_score = command.score(ctx)
        self.item_score, self.items = item.plan.compute(ctx, command)
        self.score = self.command_score + self.item_score

    def execute(self, ctx: Context):
        if self.items:
            scene = ItemMenuScene.enter(ctx)
            remains = scene.use_items(ctx, self.items)
            if remains:
                LOGGER.info("not found items", remains)
                ctx.do_recognize = True
                raise ItemNotFound()
        self.command.execute(ctx)

    def explain(self) -> Text:
        msg = ""
        if self.items:
            msg += f"{self.item_score:.2f} by {','.join(str(i) for i in self.items)};"
        return msg


def _handle_turn(ctx: Context):
    scene = CommandScene.enter(ctx)
    scene.recognize(ctx)

    # see training before shop
    turn_commands = tuple(commands.from_context(ctx))
    handle_shop = True
    for turn_command in turn_commands:
        if isinstance(turn_command, RaceCommand):
            handle_shop = False
            break

    if not ctx.disable_shopping_on_race_day or handle_shop or ctx.do_shopping:
        _handle_item_list(ctx, scene)
        _handle_shop(ctx, scene)
        
    if ctx.items_last_updated_turn == 0:
        _handle_item_list(ctx, scene)
    if ctx.turn_count_v2() in [43,55]:
        _handle_skill(ctx, scene, True)        
    if ctx.turn_count_v2() in [22,31,43, 55]:
        _handle_skill(ctx, scene)
    #if ctx.turn_count_v2() in [15,25,49]:
    #    ctx.go_out_options = ()
    for i in ctx.items:
        LOGGER.info("item:\t#%s\tx%s\t%s", i.id, i.quantity, i.name)
    command_plans = sorted(
        (_CommandPlan(ctx, i) for i in turn_commands),
        key=lambda x: x.score,
        reverse=True,
    )
    for cp in command_plans:
        LOGGER.info("score:\t%2.2f\t%s;%s", cp.score, cp.command.name(), cp.explain())
    if ((ctx.turn_count() >= 48 or ctx.is_summer_camp) and (not isinstance(command_plans[0].command, RaceCommand)) and (command_plans[0].score < 40 or (isinstance(command_plans[0].command,TrainingCommand) and len(command_plans[0].command.training.partners)<2)) and ctx.items.get(42).quantity>=1 and ctx.mood[0] > 1.0 and ctx.items.get(45).quantity>=1 and (ctx.items.get(50).quantity>=1 or ctx.items.get(17).quantity>=1 or ctx.items.get(18).quantity>=1 or ctx.items.get(19).quantity>=1 or ctx.vitality >= 0.5)):
        scene = ItemMenuScene.enter(ctx)
        remains = scene.use_items(ctx, [ctx.items.get(42)])
        ctx.scene = scenes.UnknownScene()
        return
    ctx.next_turn()
    LOGGER.info("context: %s", ctx)
    try:
        command_plans[0].execute(ctx)
    except (RaceTurnsIncorrect, ItemNotFound, ValueError):
        ctx.fail_count += 1
        ctx.scene = scenes.UnknownScene()
        time.sleep(2.0)
    except:
        ctx.fail_count += 1
        ctx.scene = scenes.UnknownScene()
        time.sleep(2.0)
        if ctx.fail_count >= 5:
            raise Exception('failed too many times')
        #_handle_turn(ctx)


class _ActionContext:
    def __init__(
        self, ctx: Context, tmpl: template.Specification, pos: _Vector2
    ) -> None:
        self.ctx = ctx
        self.tmpl = tmpl
        self.pos = pos


_Template = Union[Text, template.Specification]
_Vector2 = Tuple[int, int]
_Handler = Callable[[_ActionContext], None]


def _pass(ac: _ActionContext):
    pass


def _tap(ac: _ActionContext):
    action.tap(ac.pos)


def _cancel(ac: _ActionContext):
    action.wait_tap_image(templates.CANCEL_BUTTON)


def _close(ac: _ActionContext):
    action.wait_tap_image(templates.CLOSE_BUTTON)


def _ac_handle_turn(ac: _ActionContext):
    try:
        action.wait_image_stable(ac.tmpl, timeout=3)
    except TimeoutError:
        LOGGER.warning("command scene enter timeout, return to main loop")
        return
    _handle_turn(ac.ctx)


class _SingleModeEnd(StopIteration):
    pass


def _handle_end(ac: _ActionContext):
    ctx = ac.ctx
    LOGGER.info("end: %s", ctx)
    config.on_single_mode_end(ctx)
    raise _SingleModeEnd


def _handle_fan_not_enough(ac: _ActionContext):
    ctx = ac.ctx

    def _set_target_fan_count():
        ctx.target_fan_count = max(ctx.fan_count + 1, ctx.target_fan_count)

    ctx.defer_next_turn(_set_target_fan_count)
    action.wait_tap_image(templates.CANCEL_BUTTON)


def _handle_target_race(ac: _ActionContext):
    ctx = ac.ctx
    scene = CommandScene.enter(ctx)
    scene.recognize(ctx)
    _handle_item_list(ctx, scene)
    _handle_shop(ctx, scene)
    ctx.next_turn()
    try:
        scene = RaceMenuScene().enter(ctx)
    except RaceTurnsIncorrect:
        scene = RaceMenuScene().enter(ctx)
    cp = _CommandPlan(
        ctx, commands.RaceCommand(scene.first_race(ctx), selected=True)
    )
    LOGGER.info("score:\t%2.2f\t%s;%s", cp.score, cp.command.name(), cp.explain())
    cp.execute(ctx)


def _ac_handle_option(ac: _ActionContext):
    _handle_option()


def _handle_crane_game(ac: _ActionContext):
    ctx = ac.ctx
    config.on_single_mode_crane_game(ctx)


def _set_scenario(scenario: Text, _handler: _Handler) -> _Handler:
    def _func(ac: _ActionContext):
        ac.ctx.scenario = scenario
        _handler(ac)

    return _func


def _handle_aoharu_team_race(ac: _ActionContext):
    ctx = ac.ctx
    scene = AoharuMainScene.enter(ctx)
    scene.recognize()
    scene.go_race()

    if scene.is_final:
        action.wait_tap_image(templates.SINGLE_MODE_AOHARU_FINAL_BATTLE_BUTTON)
    else:
        for index in range(3):
            scene = AoharuCompetitorScene.enter(ctx)
            scene.choose_competitor(index)
            action.wait_tap_image(templates.GREEN_BATTLE_BUTTON)
            scene = AoharuBattleConfirmScene.enter(ctx)
            scene.recognize_predictions()
            if (
                len(
                    tuple(
                        i
                        for i in scene.predictions.values()
                        if i in (RacePrediction.HONNMEI, RacePrediction.TAIKOU)
                    )
                )
                >= 3
            ):
                break

    action.wait_tap_image(templates.GREEN_BATTLE_BUTTON)
    tmpl, pos = action.wait_image(
        templates.SINGLE_MODE_AOHARU_RACE_RESULT_BUTTON,
        templates.SINGLE_MODE_AOHARU_MAIN_RACE_BUTTON,
    )
    action.tap(pos)
    if tmpl.name == templates.SINGLE_MODE_AOHARU_MAIN_RACE_BUTTON:
        action.wait_tap_image(templates.GO_TO_RACE_BUTTON)
        action.wait_tap_image(templates.RACE_START_BUTTON)

    while True:
        tmpl, pos = action.wait_image(
            templates.SKIP_BUTTON,
            templates.SINGLE_MODE_RACE_NEXT_BUTTON,
        )
        action.tap(pos)
        if tmpl.name == templates.SINGLE_MODE_RACE_NEXT_BUTTON:
            break


def _template_actions(ctx: Context) -> Iterator[Tuple[_Template, _Handler]]:
    yield templates.CONNECTING, _pass
    yield templates.RETRY_BUTTON, _tap
    #yield templates.SINGLE_MODE_SKILL_GET_BUTTON, _tap
    yield templates.RETURN_BUTTON, _tap
    yield templates.CLOSE_BUTTON, _tap
    yield templates.CANCEL_BUTTON, _tap
    yield templates.GREEN_OK_BUTTON, _tap
    yield templates.GREEN_TIGHT_OK_BUTTON, _tap
    yield templates.SINGLE_MODE_COMMAND_TRAINING, _ac_handle_turn
    yield templates.SINGLE_MODE_FANS_NOT_ENOUGH, _handle_fan_not_enough
    yield templates.SINGLE_MODE_TARGET_RACE_NO_PERMISSION, _handle_fan_not_enough
    yield templates.SINGLE_MODE_TARGET_UNFINISHED, _cancel
    yield templates.SINGLE_MODE_FINISH_BUTTON, _handle_end
    yield templates.SINGLE_MODE_FORMAL_RACE_BANNER, _handle_target_race
    yield templates.SINGLE_MODE_RACE_NEXT_BUTTON, _tap
    yield templates.SINGLE_MODE_OPTION1, _ac_handle_option
    yield templates.GREEN_NEXT_BUTTON, _tap
    yield templates.SINGLE_MODE_URA_FINALS, _handle_target_race
    yield templates.SINGLE_MODE_GENE_INHERIT, _tap
    yield templates.SINGLE_MODE_CRANE_GAME_BUTTON, _handle_crane_game
    if ctx.scenario in (ctx.SCENARIO_AOHARU, ctx.SCENARIO_UNKNOWN):
        yield templates.SINGLE_MODE_AOHARU_AUTO_FORMATION_TITLE, _set_scenario(
            ctx.SCENARIO_AOHARU, _close
        )
        yield templates.SINGLE_MODE_AOHARU_FORMAL_RACE_BANNER, _set_scenario(
            ctx.SCENARIO_AOHARU, _handle_aoharu_team_race
        )
    if ctx.scenario in (ctx.SCENARIO_CLIMAX, ctx.SCENARIO_UNKNOWN):
        yield templates.SINGLE_MODE_GO_TO_SHOP_BUTTON, _set_scenario(
            ctx.SCENARIO_CLIMAX, _cancel
        )
        yield templates.SINGLE_MODE_TARGET_GRADE_POINT_NOT_ENOUGH, _set_scenario(
            ctx.SCENARIO_CLIMAX, _cancel
        )


def _spec_key(tmpl: _Template) -> Text:
    if isinstance(tmpl, template.Specification):
        return tmpl.name
    return tmpl


def nurturing():
    ctx = Context.new()

    while True:
        spec = {_spec_key(k): v for k, v in _template_actions(ctx)}
        tmpl, pos = action.wait_image(*spec.keys())
        ac = _ActionContext(ctx, tmpl, pos)
        try:
            spec[_spec_key(tmpl)](ac)
        except _SingleModeEnd:
            break
        except TimeoutError:
            ctx.scene = scenes.UnknownScene()
            continue
