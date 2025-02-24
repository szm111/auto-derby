import auto_derby


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.plugin.install("afk")
        #auto_derby.plugin.install("custom_race_short_mile_middle")
        auto_derby.plugin.install("custom_race_mile_middle_long")
        #auto_derby.plugin.install("custom_race_middle_long")
        auto_derby.plugin.install("custom_item")
        auto_derby.plugin.install("custom_context")
        auto_derby.plugin.install("custom_training_partner_score")
        #auto_derby.plugin.install("SSR樫本理子")
        auto_derby.plugin.install("皇团")
        # TODO: Add a plugin for setting skills
        # For now. You can set them in
        # auto_derby/data/single_mode_skills.jsonl
        # Note that skill list is missing. What missed in the file means I didn't add a ocr result for it. It means it can't be detected.
        # If you want to add skills not in the list, please disable "no_skill_prompt" in "afk" plugin. When detect skills not in the list, it will automatically add it to label file and skill file.
        # You just need to update attribute by yourself.
        
        # Skill picking up only happens at turn 22,31,43,55. Please go to auto_derby/jobs/nurturing to change it.
        
        # pick = 3 means will be picked no matter what default running style.
        # pick = 2 means it will be picked only when this skill running style is equal to your default running style
        # pick =1 TODO
        # pick = 0 Do not pick
        # All other attribute definition can be found in auto_derby/constants.py


auto_derby.plugin.register(__name__, Plugin())
