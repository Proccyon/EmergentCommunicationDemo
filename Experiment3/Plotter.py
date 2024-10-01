
#-----Imports-----#
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
#from Optimizer import Settings, Results

def readResults():

    settingsArray = []
    resultsArray = []

    i = 1
    while True:

        folderPath = "SimResults" + str(i)
        i += 1

        if not os.path.isdir(folderPath):
            return settingsArray, resultsArray

        with open(folderPath + "/Settings.txt", 'r') as settingsFile:
            settings = settingsFile.read()

        settingsArray.append(settings)

        resultsArray.append([])

        j = 1
        while True:
            resultsPath = folderPath + "/Run" + str(j)
            j += 1

            if not os.path.isdir(resultsPath):
                break

            with open(resultsPath + "/PickledResults.obj", 'rb') as resultsFile:
                results = pickle.load(resultsFile)

            resultsArray[-1].append(results)

    return settingsArray, resultsArray

def plotScore(results):

    avgScore = np.average(results.scoreArray, axis=1)
    maxScore = np.amax(results.scoreArray, axis=1)

    plt.plot(avgScore, color="green",label="avgScore")
    plt.plot(maxScore, color="red", label="maxScore")

    plt.xlabel("runs")
    plt.ylabel("score")

    plt.xlim(0, len(avgScore)-1)
    plt.ylim(0, 1.2 * np.amax(results.scoreArray))

    plt.grid(linestyle="--", alpha=0.5)

    plt.legend()

    plt.show()

def plotSize(results):

    sizeArray = [[automata.size() for automata in automataList] for automataList in results.automataArray]
    avgSize = np.average(sizeArray, axis=1)
    minSize = np.amin(sizeArray, axis=1)
    maxSize = np.amax(sizeArray, axis=1)

    plt.plot(avgSize, color="green",label="avgSize")
    plt.plot(minSize, color="blue",label="minSize")
    plt.plot(maxSize, color="red",label="maxSize")

    plt.xlabel("runs")
    plt.ylabel("size")

    plt.xlim(0, len(avgSize)-1)
    plt.ylim(0, 1.2 * np.amax(maxSize))

    plt.grid(linestyle="--", alpha=0.5)

    plt.legend()

    plt.show()

def printBestAutomata(results):

    for i in range(len(results.scoreArray)):
        jMax = np.argmax(results.scoreArray[i, :])
        bestAutomata = results.automataArray[i, jMax]
        score = results.scoreArray[i, jMax]

        print(f"#---Best-Automata-{i}-Score-{score}---#\n{bestAutomata.toString()}")


if __name__ == "__main__":

    settingsArray, resultsArray = readResults()
    results = resultsArray[3][0]

    # plotScore(results)
    # plotSize(results)
    #
    # printBestAutomata(results)

    for arr in results.automataArray:
        for automata in arr:
            a = automata.toString()



