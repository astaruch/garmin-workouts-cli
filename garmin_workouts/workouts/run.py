

class Run():
    def __init__(self):
        self.sportTypeId = 1
        self.sportTypeKey = "running"

        self.workoutName = "Run Workout"

        self.workoutSegments = [
            {
                segmentOrder: 1,
                sportType: {
                    sportTypeId: 1,
                    sportTypeKey: "running"
                },
                workoutSteps: []
            }
        ]

    def set_name(self, name):
        self.workoutName = name
