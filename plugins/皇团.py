from typing import Callable, List
import auto_derby
from auto_derby.single_mode import Context


_NAME = ['','','','','','']
_NAME[0] = "シンボリルドルフ"
_NAME[1] = "トウカイテイオー"
_NAME[2] = "ツルマルツヨシ"
_NAME[3] = "玉座に集いし者たち"
_NAME[5] = "樫本理子"

_VIT = [0, 0, 0, 0, 0,0, 0, 0, 0, 0]
_MOOD = [0, 0, 0, 0, 0,0, 0, 0, 0, 0]
_HEAL = [0, 0, 0, 0, 0,0, 0, 0, 0, 0]
_SPD = [0, 0, 0, 0, 0,0, 0, 0, 0, 0]
_STA = [0, 0, 0, 0, 0,0, 0, 0, 0, 0]
_POW = [0, 0, 0, 0, 0,0, 0, 0, 0, 0]
_GUT = [0, 0, 0, 0, 0,0, 0, 0, 0, 0]
_WIS = [0, 0, 0, 0, 0,0, 0, 0, 0, 0]
_SKILL = [0, 0, 0, 0, 0,0, 0, 0, 0, 0]


# https://gamewith.jp/uma-musume/article/show/292758

## 歌には想いを乗せて（お出かけ1）
# 体力+30～32
_VIT[0] = 13
# スタミナ(耐力)+12～13
_MOOD[0] = 1
_WIS[0] = 36
# 樫本理子の絆ゲージ+5


## ひとときの休息を（お出かけ2）
# 体力+24～26
_VIT[1] = 13
# やる気(干劲)アップ(提升)
_MOOD[1] = 1
# スタミナ(耐力)+12～13
_SPD[1] = 24
# 根性(毅力)+12～13

## 喜ぶ顔を思い浮かべて（お出かけ3）
### ここは『大容量ハチミルク』で！
# 体力+24～26
_VIT[2] = 36
# 根性+6
_SKILL[2] = 18
# 樫本理子の絆ゲージ+5
### やはり『ウマスタ映えソーダ』で！
# スキルpt+37～40
# やる気アップ
# 樫本理子の絆ゲージ+5

## 向けられる想いと戸惑い（お出かけ4）
# 体力+24～26
_VIT[3] = 26
_MOOD[3] = 1
# やる気アップ
_SPD[3] = 12
# スタミナ+6
_WIS[3] = 30
# パワー+6
_SKILL[3] = 18
# 樫本理子の絆ゲージ+5

## 胸の内を少しだけ（お出かけ5）
### 成功時：
# 体力+30～32
_VIT[4] = 26
# やる気アップ
_MOOD[4] = 1
# スタミナ+12～13
_SPD[4] = 18
# 根性+12～13
_WIS[4] = 36
_SKILL[4] = 24
# 『一陣の風』のヒントLv+3
# 樫本理子の絆ゲージ+5
### 失敗時：
# 体力+30～32
# やる気アップ
# スタミナ+6
# 根性+6
# 『一陣の風』のヒントLv+1
# 樫本理子の絆ゲージ+5

## 歌には想いを乗せて（お出かけ1）
# 体力+30～32
_VIT[5] = 30
# やる気(干劲)アップ(提升)
_MOOD[5] = 1
# スタミナ(耐力)+12～13
_STA[5] = 12
# 樫本理子の絆ゲージ+5


## ひとときの休息を（お出かけ2）
# 体力+24～26
_VIT[6] = 25
# やる気(干劲)アップ(提升)
_MOOD[6] = 1
# スタミナ(耐力)+12～13
_STA[6] = 12
# 根性(毅力)+12～13
_GUT[6] = 12
# 樫本理子の絆ゲージ+5

## 喜ぶ顔を思い浮かべて（お出かけ3）
### ここは『大容量ハチミルク』で！
# 体力+24～26
_VIT[7] = 25
# やる気アップ
_MOOD[7] = 1
# スタミナ+12～13
_STA[7] = 12
# 根性+6
_GUT[7] = 6
# 樫本理子の絆ゲージ+5
### やはり『ウマスタ映えソーダ』で！
# スキルpt+37～40
# やる気アップ
# 樫本理子の絆ゲージ+5

## 向けられる想いと戸惑い（お出かけ4）
# 体力+24～26
_VIT[8] = 25
# やる気アップ
_MOOD[8] = 1
# スピード+12～13
_SPD[8] = 12
# スタミナ+6
_STA[8] = 6
# パワー+6
_POW[8] = 6
# 樫本理子の絆ゲージ+5

## 胸の内を少しだけ（お出かけ5）
### 成功時：
# 体力+30～32
_VIT[9] = 31
# やる気アップ
_MOOD[9] = 1
# スタミナ+12～13
_STA[9] = 12
# 根性+12～13
_GUT[9] = 12
# 『一陣の風』のヒントLv+3
# 樫本理子の絆ゲージ+5
### 失敗時：
# 体力+30～32
# やる気アップ
# スタミナ+6
# 根性+6
# 『一陣の風』のヒントLv+1
# 樫本理子の絆ゲージ+5


class Plugin(auto_derby.Plugin):
    """
    Use this when friend cards include SSR樫本理子.
    Multiple friend type support card is not supported yet.
    """

    def install(self) -> None:
        auto_derby.config.single_mode_go_out_names.update(_NAME)

        class Option(auto_derby.config.single_mode_go_out_option_class):
            def heal_rate(self, ctx: Context) -> float:
                if self.name not in _NAME:
                    return super().heal_rate(ctx)

                c = _NAME.index(self.name)
                return _HEAL[c + self.current_event_count]

            def mood_rate(self, ctx: Context) -> float:
                if self.name not in _NAME:
                    return super().mood_rate(ctx)

                c = _NAME.index(self.name)
                return _MOOD[c + self.current_event_count]

            def vitality(self, ctx: Context) -> float:
                if self.name not in _NAME:
                    return super().vitality(ctx)

                c = _NAME.index(self.name)
                return _VIT[c + self.current_event_count] / ctx.max_vitality

            def score(self, ctx: Context) -> float:
                ret = super().score(ctx)
                if self.name != _NAME:
                    return ret

                t = Training()
                c = _NAME.index(self.name)
                c = c + self.current_event_count
                t.speed = _SPD[c]
                t.stamina = _STA[c]
                t.power = _POW[c]
                t.guts = _GUT[c]
                t.wisdom = _WIS[c]
                t.skill = _SKILL[c]
                ret += t.score(ctx)

                return ret

        auto_derby.config.single_mode_go_out_option_class = Option


auto_derby.plugin.register(__name__, Plugin())
