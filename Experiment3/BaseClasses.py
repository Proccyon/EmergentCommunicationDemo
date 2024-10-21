
#-----Imports-----#


class Brain:

    def __init__(self):
        pass

    def run(self, sim, agent):
        pass

    def toString(self) -> str:
        return ""

    def copy(self):
        return Brain()

    def mutate(self, op):
        return self

    def createOffspring(self, op):
        child = self.copy()
        child.mutate(op)
        return child


class Component:

    def __init__(self):
        self.type = "base"

    def run(self, sim, agent) -> bool:
        return False

    def toString(self) -> str:
        return ""

