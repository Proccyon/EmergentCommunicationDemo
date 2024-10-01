
#-----Imports-----#
import numpy as np
from Map import CircleMap, FourRoomsMap
from Simulation import runSimHidden
from Automata import Automata
from Parallelizer import runAsync
from Conditions import OptimizationParameters
from Saver import save
import time
from MutationMethods import *

class Settings:

    def __init__(self, map, baseAutomata, op):
        self.map = map
        self.baseAutomata = baseAutomata
        self.op = op

    def toString(self):
        return (f"#---OptimizationParameters---#\n"
                f"{self.op.toString()}\n"
                f"#---Map---#\n"
                f"{self.map.toString()}\n"
                f"#---BaseAutomata---#\n"
                f"{self.baseAutomata.toString()}")

class Results:

    def __init__(self, scoreArray, automataArray):
        self.scoreArray = scoreArray
        self.automataArray = automataArray


def TournamentSelection(automataList, scoreList, tournamentSize=3):
    selectedIndices = np.random.choice(range(len(automataList)), size=tournamentSize)
    imax = np.argmax([scoreList[ind] for ind in selectedIndices])
    return automataList[selectedIndices[imax]]

def run(i, map, automataList, tMax):

    score = runSimHidden(i, map, automataList[i], tMax)
    return score

def optimize(map, baseAutomata, op):
    print("Starting simulations...")

    scoreArray = np.zeros((op.runs, op.n), dtype=int)
    automataArray = np.empty((op.runs, op.n), dtype=Automata)
    automataList = [baseAutomata.createOffspring(op) for _ in range(op.n)]

    bestAutomata = baseAutomata
    bestScore = 0

    for i in range(op.runs):

        # Run simulations to determine performance of each automata
        scoreList = runAsync(run, op.n, [map, automataList, op.tMax])

        # Remember best performing automata
        iMax = np.argmax(scoreList)
        if scoreList[iMax] > bestScore:
            bestScore = scoreList[iMax]
            bestAutomata = automataList[iMax]
            print(f"New Best Automata:\n{bestAutomata.toString()}")

        # Save the results
        scoreArray[i, :] = scoreList
        automataArray[i, :] = automataList

        # Select new population based on performance and mutate selected automata
        newAutomataList = []
        for _ in range(op.n):
            if np.random.random() < op.elitismChance:
                automata = bestAutomata.createOffspring(op)
            else:
                automata = TournamentSelection(automataList, scoreList).createOffspring(op)
            newAutomataList.append(automata)

        automataList = newAutomataList
        avgSize = np.round(np.average([automata.size() for automata in automataList]), 2)

        print(f"Run {i+1}/{op.runs}, minScore={np.amin(scoreList)}, maxScore={np.amax(scoreList)}, avgScore={np.average(scoreList)}, avgSize={avgSize}")


    # Save results
    settings = Settings(map, baseAutomata, op)
    results = Results(scoreArray, automataArray)
    save(settings, results)



if __name__ == "__main__":

    op = OptimizationParameters()
    op.tMax = 800
    op.runs = 100
    op.n = 100
    creatureCount = 15

    map = FourRoomsMap(6, 6, 6, 1, creatureCount, 10, 1, 2, 3, 4).init()

    automata = Automata().initBaseAutomata()

    optimize(map, automata, op)








