
#-----Imports-----#
from BaseClasses import Brain, Component
import numpy as np
from Conditions import *
from Actions import *
from TaskNode import *

class Lister(Component):

    def __init__(self):
        Component.__init__(self)
        self.type = "lister"
        self.componentList = []

    def add(self, component: Component):
        self.componentList.append(component)

    def get(self, i):
        if i < 0 or i >= len(self.componentList):
            print("Getting component out of range")
            return None
        else:
            return self.componentList[i]

class Sequence(Lister):

    def run(self, sim, agent) -> bool:

        if agent.isDone:
            return True

        for component in self.componentList:
            if agent.isDone:
                return True
            if not component.run(sim, agent):
                return False
        return True

    def toString(self, i=0) -> str:
        return "Sequence"


class Selector(Lister):

    def run(self, sim, agent) -> bool:

        if agent.isDone:
            return True

        for component in self.componentList:
            if agent.isDone:
                return True
            if component.run(sim, agent):
                return True
        return False

    def toString(self, i=0) -> str:
        return "Selector"


class BehaviourTree(Brain):

    def __init__(self):
        Brain.__init__(self)
        self.root = None

    def initBaseTree(self):
        self.root = Selector()
        c1 = Sequence()
        c1.add(IsHoldingFood("self"))
        c1.add(ReturnHomeNode())
        self.root.add(c1)
        c2 = Sequence()
        c2.add(GreaterThan(NearbyFoodAmount("self"), Constant(0)))
        c2.add(GatherNode())
        self.root.add(c2)
        c3 = RandomWalkNode()
        self.root.add(c3)
        return self

    def initMemorizingTree(self):
        self.root = Selector()
        c1 = Sequence()
        c1.add(IsHoldingFood("self"))
        c1.add(ReturnHomeNode())
        self.root.add(c1)
        c2 = Sequence()
        c2.add(GreaterThan(NearbyFoodAmount("self"), Constant(0)))
        c2.add(SetWaypoint())
        c2.add(GatherNode())
        self.root.add(c2)
        c3 = Sequence()
        c3.add(IsWaypointSet("self"))
        c3.add(GoToWaypoint())
        self.root.add(c3)
        c4 = Sequence()
        c4.add(ResetWaypoint())
        c4.add(RandomWalkNode())
        self.root.add(c4)
        return self

    def initCommunicatingAgent(self):

        self.root = Sequence()
        self.root.add()

        s1 = Selector()
        c1 = Sequence()
        c1.add(IsHoldingFood("self"))
        c1.add(ReturnHomeNode())
        self.root.add(c1)
        c2 = Sequence()
        c2.add(GreaterThan(NearbyFoodAmount("self"), Constant(0)))
        c2.add(SetWaypoint())
        c2.add(GatherNode())
        self.root.add(c2)
        c3 = Sequence()
        c3.add(IsWaypointSet("self"))
        c3.add(GoToWaypoint())
        self.root.add(c3)
        c4 = Sequence()
        c4.add(ResetWaypoint())
        c4.add(RandomWalkNode())
        self.root.add(c4)
        return self


    def run(self, sim, agent):
        agent.isDone = False
        self.root.run(sim, agent)

    def toString(self) -> str:

        nextComps = [self.root]

        text = "digraph G {\nnodesep=0.5\nranksep=0.5\n"
        i = 0
        while len(nextComps) > 0:
            component = nextComps.pop(0)
            if component.type == "condition":
                color = '"#a1dd80"'
            elif component.type == "action":
                color = '"#ddb380"'
            elif component.type == "task":
                color = '"#dd8080"'
            else:
                if component.toString() == "Selector":
                    color = '"#dadd80"'
                else:
                    color = '"#80d4dd"'

            text += f'n{i} [label="{component.toString()}",style=filled,shape=rect,fillcolor={color}]\n'

            if component.type == "lister":
                j = i + len(nextComps) + 1
                for child in component.componentList:
                    nextComps.append(child)
                    text += f'n{i}->n{j}\n'
                    j += 1
            i += 1
        text += "}"
        return text

    def copy(self):
        pass

    def mutate(self, op):
        pass


