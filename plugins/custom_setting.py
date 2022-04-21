import auto_derby


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.plugin.install("afk")
        auto_derby.plugin.install("custom_race_mile_middle_long")
        auto_derby.plugin.install("custom_item")
        auto_derby.plugin.install("custom_context")


auto_derby.plugin.register(__name__, Plugin())
