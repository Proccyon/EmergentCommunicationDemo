
#-----Imports-----#
import numpy as np
from Map import CircleMap, FourRoomsMap
from Simulation import runSimHidden
from Automata import Automata
from Parallelizer import runAsync

class OptimizationParameters:

    def __init__(self):
        self.pNOT = 0.1
        self.pConst = 0.25
        self.pTargetSelf = 0.8
        self.constMin = 0
        self.constMax = 10
        self.conditionAmountMutateRate = 0.1
        self.conditionMutateRate = 0.1
        self.finEdgeMutationRate = 0.1
        self.actionMutationRate = 0.1




def run(i, map, automataList, tMax):

    score = runSimHidden(i, map, automataList[i], tMax)
    #print(f"automata {i + 1}/{n}, score = {score}")
    return score

def optimize(map, baseAutomata, tMax, n, runs):
    print("Starting simulations...")

    automata = baseAutomata
    for i in range(runs):
        print(f"Run {i+1}/{runs}")

        automataList = [automata.createOffspring() for _ in range(n)]

        scoreList = runAsync(run, n, [map, automataList, tMax])

        automata = automataList[np.argmax(scoreList)]

if __name__ == "__main__":
    print("Initializing map...")
    map = FourRoomsMap(6,6,6,1,15,10,1,2,3,4).init()
    op = OptimizationParameters()

    automata = Automata().initBaseAutomata()
    tMax = 4000
    n = 5
    runs = 10

    optimize(map, automata, tMax, n, runs)




