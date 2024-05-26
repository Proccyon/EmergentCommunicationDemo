
#-----Import-----#
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os

from Saver import Log


def pastAverage(array, window):
    n = len(array)

    if window > n:
        return np.average(array)
    else:
        return np.average(array[n - window:n])

def slidingWindow(array, window):
    return np.array([pastAverage(array[0:i], window) for i in range(len(array))])


def readResults():

    settingsArray = []
    resultsArray = []

    i = 1
    while True:

        folderPath = "SimResults" + str(i)
        i += 1

        if not os.path.isdir(folderPath):
            return settingsArray, resultsArray

        with open(folderPath + "/pickledSettings.obj", 'rb') as settingsFile:
            settings = pickle.load(settingsFile)

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


settingsArray, resultsArray = readResults()


def plotEnergyEaten(index, window):

    results = resultsArray[index]
    settings = settingsArray[index]

    Tfood = np.pi * (2/3) / settings.vars["poisonChangeRate"]


    posEnergyArray = np.array([result.vars["posEnergyEatenLog"].log for result in results])
    negEnergyArray = np.array([result.vars["negEnergyEatenLog"].log for result in results])

    avgPosEnergy = slidingWindow(np.average(posEnergyArray, axis=0), window)
    stdPosEnergy = slidingWindow(np.std(posEnergyArray, axis=0), window)
    avgNegEnergy = slidingWindow(np.average(negEnergyArray, axis=0), window)
    stdNegEnergy = slidingWindow(np.std(negEnergyArray, axis=0), window)

    n = len(avgPosEnergy)

    t = np.arange(n) / Tfood

    plt.figure()

    plt.plot(t, avgPosEnergy, color="green", label="p(eat|dE>0)")
    plt.plot(t, avgNegEnergy, color="red", label="p(eat|dE<0)")

    plt.title(f"Probability of eating positive and negative food for Tfood={Tfood}")
    plt.xlabel("T(Food periods)")
    plt.ylabel("Probability of eating")

    plt.fill_between(t, avgPosEnergy - stdPosEnergy, avgPosEnergy + stdPosEnergy, color="green", alpha=0.5)
    plt.fill_between(t, avgNegEnergy - stdNegEnergy, avgNegEnergy + stdNegEnergy, color="red", alpha=0.5)

    plt.xlim(0, np.amax(t))
    plt.ylim(0, 1.1)

    plt.grid(linestyle="--", alpha=0.5, color="black")

    plt.legend()

    plt.show()



#-----Main-----#

plotEnergyEaten(6, 200)

