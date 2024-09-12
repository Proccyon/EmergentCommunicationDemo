#-----Imports-----#


class Settings:

    def __init__(self, sim):

        self.vars = {"creatureSpawnChance": sim.creatureSpawnChance,
                     "creatureInitEnergy": sim.creatureInitEnergy,
                     "creatureOffspringEnergy": sim.creatureOffspringEnergy,
                     "creatureDrainEnergy": sim.creatureDrainEnergy,
                     "creatureSmellRange": sim.smellRange,
                     "foodSpawnChance": sim.foodSpawnChance,
                     "foodInitEnergy": sim.foodInitEnergy,
                     "poisonChangeRate": sim.poisonChangeRate,
                     "poisonStd": sim.poisonStd,
                     "poisonOffset": sim.poisonOffset,
                     "memorySize": sim.memorySize,
                     "memoryUpdateRate": sim.memoryUpdateRate,
                     "mutateStd": sim.mutateStd,
                     "mutateP": sim.mutateP,
                     "memoryShareChance": sim.memoryShareChance,
                     "memoryHiddenSizes": sim.memoryHiddenSizes,
                     "decisionHiddenSizes": sim.decisionHiddenSizes,
                     "totalSteps": sim.totalSteps}

    def __eq__(self, other):
        if not isinstance(other, Settings):
            return False

        if len(self.vars.keys()) != len(other.vars.keys()):
            return False

        for key, var in self.vars.items():

            if key not in other.vars or self.vars[key] != other.vars[key]:
                return False

        return True

class Results:

    def __init__(self, sim):

        self.vars = {
            "energyEatenLog": sim.energyEatenLog,
            "posEnergyEatenLog": sim.posEnergyEatenLog,
            "negEnergyEatenLog": sim.negEnergyEatenLog
        }










