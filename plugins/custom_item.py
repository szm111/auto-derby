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
                
                # You can find all item settings at auto_derby/data/single_mode_items.jsonl.
                # Suggest to use item id as identifier
                
                # Add more score for speed ankle weight. Only buy speed and power ankle weights
                if es.training_vitality_debuff:
                    if TrainingType.SPEED in es.training_vitality_debuff:
                        ret += 50
                    elif TrainingType.POWER not in es.training_vitality_debuff:
                        ret = 0
                    
                # Do not bug 20% Megaphone. Only buy 40% and 60%. 60% has very high priority.
                if es.training_effect_buff and not es.training_vitality_debuff:
                    tp, value, _, _ = self.effects[0].values
                    if value < 30:
                        ret = 0
                    elif value>50:
                        ret += 100
                        
                # All efficient books
                if es.speed >5 or es.power>5 or es.statmia >5 or es.guts > 5 or es.wisdom > 5:
                    ret += 100
                    
                # All horseshoe hammers.
                if es.race_reward_buff:
                    ret += 100
                
                # Vitality items and amulet
                if es.training_no_failure or (es.vitality and not es.mood):
                    ret += 100
                    
                # Cakes
                if es.mood:
                    ret += 100
                    
                # BBQ and PHD hat
                if self.id == 29 or self.id == 25:
                    ret += 100
                    
                # Only buy speed training level. 
                if es.training_levels:
                    if self.id ==37:
                        ret+=100
                    else:
                        ret = 0
                        
                # Do not buy maximum vitality itemss.
                if es.max_vitality:
                    ret = 0
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
                
                # There are bugs in detecting race in URA. Use this as a temorary solution to use horseshoe hammer
                if isinstance(command, RaceCommand) and ctx.date[0] in [0,4] and es.race_reward_buff:
                    if summary.race_reward_buff:
                        ret += (es.race_reward_buff.total_rate()*100 - summary.race_reward_buff.total_rate()*100) *3
                    else:
                        ret += es.race_reward_buff.total_rate()*100 * 3

                return ret

            # If effect_score is higher than expected_effect_score, it will use the item
            def expected_effect_score(self, ctx: Context, command: Command) -> float:
                ret = super().expected_effect_score(ctx, command)
                es = self.effect_summary()
                # reduce when training speed > 13
                if isinstance(command, TrainingCommand) and command.training.speed > 13:
                    ret -= self.original_price * 0.5
                
                # increase when race grade lower than G1.
                if (
                    isinstance(command, RaceCommand)
                    and command.race.grade > command.race.GRADE_G1
                ):
                    ret += 10
                
                # URA, should use item. They should be detected as G1 but there are bugs.
                if isinstance(command, RaceCommand) and ctx.date[0] == 4 and es.race_reward_buff:
                    ret =0
                    return ret
                    
                # Use small horseshoe hammer when it is G1
                if isinstance(command, RaceCommand) and command.race.grade == command.race.GRADE_G1 and es.race_reward_buff and self.id == 51:
                    ret =0
                # Use big horseshoe hammer when it is G1 and we have more than 2 (Maintain 2 for URA)
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
