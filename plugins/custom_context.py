import auto_derby
from auto_derby import single_mode


class Context(single_mode.Context):
    def __init__(self) -> None:
        super().__init__()
        # Running style for distance longer than 2600
        self.long_distance_style = RuningStyle.LEAD
        # Default Running Style
        self.default_running_style = RuningStyle.LEAD


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.single_mode_context_class = Context


auto_derby.plugin.register(__name__, Plugin())
