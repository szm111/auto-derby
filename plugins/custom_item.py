import auto_derby
from auto_derby.constants import TrainingType
from auto_derby.single_mode.commands import Command, TrainingCommand, RaceCommand
from auto_derby.single_mode import Context, condition
from auto_derby.single_mode.item import EffectSummary


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        class Item(auto_derby.config.single_mode_item_class):
            # high exchange score means high exchange priority
            def exchange_score(self, ctx: Context) -> float:
                ret = super().exchange_score(ctx)
                es = self.effect_summary()
                # increase for "プリティーミラー"
                # if self.name == "プリティーミラー":
                #    ret += 10
                
                if es.training_vitality_debuff:
                    if TrainingType.SPEED in es.training_vitality_debuff:
                        ret += 50
                    elif TrainingType.POWER not in es.training_vitality_debuff:
                        ret = 0
                    
                if es.training_effect_buff and not es.training_vitality_debuff:
                    tp, value, _, _ = self.effects[0].values
                    if value < 30:
                        ret = 0
                    elif value>50:
                        ret += 100
                        
                    
                if es.speed >5 or es.power>5 or es.statmia >5 or es.guts > 5 or es.wisdom > 5:
                    ret += 100
                    
                if es.race_reward_buff:
                    ret += 100
                
                if es.training_no_failure or (es.vitality and not es.mood):
                    ret += 100
                    
                if es.mood:
                    ret += 100
                    
                if self.id == 29 or self.id == 25:
                    ret += 100
                    
                if es.training_levels or es.max_vitality:
                    if self.id ==37:
                        ret+=100
                    else:
                        ret = 0

                # increse for item can add condition "愛嬌○"
                # if any(condition.get(i).name == "愛嬌○" for i in es.condition_add):
                #     ret += 10
                return ret

            # item will not be exchanged from shop if
            # exchange score less than expected exchange score
            def expected_exchange_score(self, ctx: Context) -> float:
                ret = super().expected_exchange_score(ctx)
                # increase for wisdom training buff
                es = self.effect_summary()
                return ret

            # effect score will be added to command score.
            # all items that effect score greater than expected effect score
            # will be used before command execute.
            # also affect default exchange score.
            def effect_score(
                self, ctx: Context, command: Command, summary: EffectSummary
            ) -> float:
                ret = super().effect_score(ctx, command, summary)
                es = self.effect_summary()
                # increase for "スピードアンクルウェイト"
                #if (
                #    isinstance(command, TrainingCommand)
                #    and command.training.type == TrainingType.SPEED
                #    and self.name == "スピードアンクルウェイト"
                #):
                #    ret += 10
                
                if isinstance(command, RaceCommand) and ctx.date[0] in [0,4] and es.race_reward_buff:
                    if summary.race_reward_buff:
                        ret += (es.race_reward_buff.total_rate()*100 - summary.race_reward_buff.total_rate()*100) *3
                    else:
                        ret += es.race_reward_buff.total_rate()*100 * 3

                return ret

            def expected_effect_score(self, ctx: Context, command: Command) -> float:
                ret = super().expected_effect_score(ctx, command)
                es = self.effect_summary()
                # reduce when training speed > 30
                if isinstance(command, TrainingCommand) and command.training.speed > 13:
                    ret -= self.original_price * 0.5
                # increase  when race grade lower than G1
                if (
                    isinstance(command, RaceCommand)
                    and command.race.grade > command.race.GRADE_G1
                ):
                    ret += 10
                    
                if isinstance(command, RaceCommand) and ctx.date[0] == 4 and es.race_reward_buff:
                    ret =0
                    return ret
                    
                if isinstance(command, RaceCommand) and command.race.grade == command.race.GRADE_G1 and es.race_reward_buff and self.id == 51:
                    ret =0
                if isinstance(command, RaceCommand) and command.race.grade == command.race.GRADE_G1 and es.race_reward_buff and self.id == 52:
                    if ctx.items.get(self.id).quantity >= 3 or ctx.date[0] in [0,4]:
                        ret =0
                    else:
                        ret += 100
                return ret

            def should_use_directly(self, ctx: Context) -> bool:
                # use max vitality item directly after exchange
                es = self.effect_summary()
                if es.max_vitality > 0:
                    return True
                if es.training_levels:
                    return True
                if es.speed >5 or es.power>5 or es.statmia >5 or es.guts > 5 or es.wisdom > 5:
                    return True
                if self.id == 29 or self.id == 25:
                    return True
                if es.mood and not es.vitality and ctx.mood[0] < 1.05:
                    return True
                return super().should_use_directly(ctx)

        auto_derby.config.single_mode_item_class = Item


auto_derby.plugin.register(__name__, Plugin())
