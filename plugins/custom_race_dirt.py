# -*- coding=UTF-8 -*-
# Code generated by auto-derby-plugin-generator 94139cf
# URL: https://natescarlet.github.io/auto-derby-plugin-generator/#/plugins/race
# Date: 3/20/2022, 9:32:23 AM

import auto_derby
from auto_derby import single_mode


from typing import Text, Dict, Tuple

_ACTION_NONE = 0
_ACTION_BAN = 1
_ACTION_LESS = 2
_ACTION_MORE = 3
_ACTION_PICK = 4

_DEFAULT_ACTION = _ACTION_BAN

_RULES: Dict[Tuple[int, Text], int] = {
    (15, "新潟ジュニアステークス"): _ACTION_PICK,
    (16, "札幌ジュニアステークス"): _ACTION_PICK,
    (18, "サウジアラビアロイヤルカップ"): _ACTION_PICK,
    (19, "アルテミスステークス"): _ACTION_PICK,
    (20, "デイリー杯ジュニアステークス"): _ACTION_PICK,
    (22, "阪神ジュベナイルフィリーズ"): _ACTION_PICK,
    (23, "全日本ジュニア優駿"): _ACTION_PICK,
    (24, "京成杯"): _ACTION_PICK,
    (26, "共同通信杯"): _ACTION_PICK,
    (28, "弥生賞"): _ACTION_PICK,
    (29, "スプリングステークス"): _ACTION_PICK,
    (30, "マリーンカップ"): _ACTION_PICK,
    (32, "NHKマイルカップ"): _ACTION_PICK,
    (33, "オークス"): _ACTION_PICK,
    (34, "関東オークス"): _ACTION_PICK,
    (36, "ジャパンダートダービー"): _ACTION_PICK,
    (37, "マーキュリーカップ"): _ACTION_PICK,
    (38, "レパードステークス"): _ACTION_PICK,
    (40, "紫苑ステークス"): _ACTION_PICK,
    (41, "さざんかテレビ杯"): _ACTION_PICK,
    (42, "レディスプレリュード"): _ACTION_PICK,
    #(42, "東京盃"): _ACTION_PICK,
    #(44, "JBCレディスクラシック"): _ACTION_PICK,
    (44, "みやこステークス"): _ACTION_PICK,
    (45, "マイルチャンピオンシップ"): _ACTION_PICK,
    (46, "チャンピオンズカップ"): _ACTION_PICK,
    (47, "東京大賞典"): _ACTION_PICK,
    (49, "東海ステークス"): _ACTION_PICK,
    (50, "川崎記念"): _ACTION_PICK,
    (51, "フェブラリーステークス"): _ACTION_PICK,
    (53, "マーチステークス"): _ACTION_PICK,
    (54, "アンタレスステークス"): _ACTION_PICK,
    (56, "かしわ記念"): _ACTION_PICK,
    (57, "平安ステークス"): _ACTION_PICK,
    (59, "帝王賞"): _ACTION_PICK,
    (60, "スパーキングレディーカップ"): _ACTION_PICK,
    (62, "エルムステークス"): _ACTION_PICK,
    (63, "札幌記念"): _ACTION_PICK,
    (65, "シリウスステークス"): _ACTION_PICK,
    (66, "マイルチャンピオンシップ南部杯"): _ACTION_PICK,
    #(68, "JBCクラシック"): _ACTION_PICK,
    (68, "武蔵野ステークス"): _ACTION_PICK,
    (69, "ジャパンカップ"): _ACTION_PICK,
    (70, "クイーン賞"): _ACTION_PICK,
    (71, "東京大賞典"): _ACTION_PICK,
}


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        class Race(auto_derby.config.single_mode_race_class):
            def score(self, ctx: single_mode.Context) -> float:
                ret = super().score(ctx)
                action = _RULES.get(
                    (ctx.turn_count(), self.name),
                    _DEFAULT_ACTION,
                )
                if self.grade == Race.GRADE_NOT_WINNING and not ctx.is_after_winning:
                    ret += 15
                    return ret
                if action == _ACTION_BAN:
                    ret = 0
                elif action == _ACTION_LESS:
                    ret -= 5
                elif action == _ACTION_MORE:
                    ret += 5
                elif action == _ACTION_PICK:
                    ret += 100
                return ret

        auto_derby.config.single_mode_race_class = Race


auto_derby.plugin.register(__name__, Plugin())
