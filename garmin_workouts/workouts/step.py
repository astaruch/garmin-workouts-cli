
class StepType:
    def __init__(self, id, key):
        self.stepType = {
            "stepTypeId": id,
            "stepTypeKey": key
        }
        if id == 6:
            self.type = "RepeatGroupDTO"
        else:
            self.type = "ExecutableStepDTO"


class WarmupStep(StepType):
    def __init__(self):
        super().__init__(1, "warmup")


class CooldownStep(StepType):
    def __init__(self):
        super().__init__(2, "cooldown")


class IntervalStep(StepType):
    def __init__(self):
        super().__init__(3, "interval")


class RecoveryStep(StepType):
    def __init__(self):
        super().__init__(4, "recovery")


class RestStep(StepType):
    def __init__(self):
        super().__init__(5, "rest")


class RepeatStep(StepType):
    def __init__(self):
        super().__init__(6, "repeat")


class OtherStep(StepType):
    def __init__(self):
        super().__init__(7, "other")
