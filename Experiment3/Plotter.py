
#-----Imports-----#
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
from Optimizer import Settings, Results, run
from AutomataTester import *
from Map import getMapDict
from Parallelizer import runAsync
from ParameterOptimizer import ParameterOptimizerSettings, ParameterOptimizerResults, Parameters
import colorsys

#-----ResultsReader-----#

def readResults(folderName):

    settingsArray = []
    resultsArray = []

    i = 1
    while True:

        folderPath = folderName + str(i)
        i += 1

        if not os.path.isdir(folderPath):
            return settingsArray, resultsArray

        with open(folderPath + "/PickledSettings.obj", 'rb') as settingsFile:
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

    return settingsArray, resultsArray

#-----OptimizerPlotter----#

def plotScore(results):

    avgScore = np.average(results.scoreArray, axis=1)
    maxScore = np.amax(results.scoreArray, axis=1)

    plt.plot(avgScore, color="green", label="avgScore")
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

def getRealScore(settings, results, runs):

    mapDict = getMapDict()
    map = mapDict[settings.mapSettings.name](settings.mapSettings).generateArrays()

    automataArray, scoreArray = results.automataArray, results.scoreArray
    bestAutomataList = []
    indList = []

    bestScore = 0
    for i in range(len(scoreArray)):
        jMax = np.argmax(scoreArray[i, :])
        maxScore = scoreArray[i, jMax]
        if maxScore > bestScore:
            bestScore = maxScore
            bestAutomataList.append(automataArray[i, jMax])
            indList.append(i)

    avgScoreList = []
    for automata in bestAutomataList:
        automataList = [automata for _ in range(runs)]
        scoreList = runAsync(run, runs, [map, automataList, settings.op.tMax])
        avgScoreList.append(np.average(scoreList))

    yList = np.full(len(scoreArray[:, 0]), avgScoreList[-1])

    prevInd = 0
    for i, ind in enumerate(indList):
        yList[prevInd:ind+1] = avgScoreList[i]
        prevInd = ind

    return yList


def plotRealScore(scoreList):

    plt.plot(scoreList, color="green")

    plt.xlabel("Generation")
    plt.ylabel("Average score of best automata")

    plt.xlim(0, len(scoreList) - 1)
    plt.ylim(0, 1.2 * np.amax(scoreList))

    plt.grid(linestyle="--", alpha=0.5)

    plt.show()

#-----PopulationExperimentPlotter-----#

def plotPopScoreGraph(settings, results, automataNames):

    scoreArray = results.scoreArray
    popRange = settings.populationRange
    maxScore = 0
    for i in range(scoreArray.shape[0]):
        avgScoreList = np.average(scoreArray[i, :, :], axis=1) / popRange
        plt.scatter(popRange, avgScoreList, s=12)
        plt.plot(popRange, avgScoreList, label=automataNames[i])
        maxScore = max(maxScore, np.amax(avgScoreList))

    plt.xlim(0, 1.05 * np.amax(popRange))
    plt.ylim(0, 1.1 * maxScore)

    plt.title(f"Score vs Population with Tmax={settings.op.tMax}, commRange={settings.simSettings.commRange}")
    plt.xlabel("Population size")
    plt.ylabel("Average Score per agent")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend(fontsize=8)

    plt.show()

#-----CommExperimentPlotter-----#

def plotCommScoreGraph(settings, results, automataNames, colorList):

    scoreArray = results.scoreArray / results.maxScore
    commRangeList = settings.commRangeList

    maxScore = 0
    for i in range(scoreArray.shape[0]):
        scoreList = scoreArray[i, :, :]
        avgScoreList = np.average(scoreList, axis=1)
        lowerBound = np.percentile(scoreList, 15.9, axis=1)
        upperBound = np.percentile(scoreList, 84.1, axis=1)

        color = colorList[i]
        plt.plot(commRangeList, avgScoreList, label=automataNames[i], color=color)
        plt.scatter(commRangeList, avgScoreList, color=color, s=12)
        plt.plot(commRangeList, lowerBound, alpha=0.1, color=color)
        plt.plot(commRangeList, upperBound, alpha=0.1, color=color)
        plt.fill_between(commRangeList, lowerBound, upperBound, alpha=0.25, color=color)
        maxScore = max(maxScore, np.amax(upperBound))

    plt.title(f"Score vs commRange with Tmax={settings.op.tMax}, population={settings.mapSettings.creatureCount}")
    plt.xlim(0, np.amax(commRangeList))
    plt.ylim(0, 1.1 * maxScore)

    plt.xlabel("Maximum communication range")
    plt.ylabel("Average Score per agent")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend(fontsize=8)

    plt.show()





def plotCommScoreGraphSingle(settings, results, color, index=0):

    fig, ax1, = plt.subplots(figsize=(10, 5))

    scoreArray = results.scoreArray / results.maxScore
    commRangeList = settings.commRangeList

    maxScore = 0
    maxDensity = np.amax(results.bestFoodDensityArray)
    avgMaxFoodReached = np.average(results.bestFoodDensityArray == maxDensity, axis=2)
    avgFoodCollected = np.average(results.foodCollectedArray, axis=2) / np.amax(results.foodCollectedArray)

    scoreList = scoreArray[index, :, :]
    avgScoreList = np.average(scoreList, axis=1)
    lowerBound = np.percentile(scoreList, 15.9, axis=1)
    upperBound = np.percentile(scoreList, 84.1, axis=1)

    line1, = ax1.plot(commRangeList, avgScoreList, label="Average score(normalized)", color=color)
    ax1.scatter(commRangeList, avgScoreList, color=color, s=12)
    ax1.plot(commRangeList, lowerBound, alpha=0.1, color=color)
    ax1.plot(commRangeList, upperBound, alpha=0.1, color=color)
    ax1.fill_between(commRangeList, lowerBound, upperBound, alpha=0.25, color=color)

    line2, = ax1.plot(avgMaxFoodReached[index,:], linestyle="--", color="black", label="p(bestFoodReached)")
    line3, = ax1.plot(avgFoodCollected[index,:], linestyle="--", color="red", label="Average food collected(normalized)")

    ax1.set_title(f"Score vs commRange with Tmax={settings.op.tMax}, population={settings.mapSettings.creatureCount}, R={settings.mapSettings.r1}")
    ax1.set_xlim(0, np.amax(commRangeList))
    ax1.set_ylim(0, 1.05)

    ax1.set_xlabel("Maximum communication range")
    ax1.set_ylabel("Fraction")

    ax1.grid(linestyle="--", alpha=0.5)

    lines = [line1, line2, line3]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper right', fontsize=8)

    plt.show()



def plotCommScoreMultSizes(settingsList, resultsList, colorList, useAUC=False, plotPopulation=False):

    maxScore = 0
    xMax = 0
    yMax = 0
    for i in range(len(settingsList)):
        settings, results, color = settingsList[i], resultsList[i], colorList[i]

        if useAUC:
            scoreArray = results.uacArray / results.maxUAC
        else:
            scoreArray = results.scoreArray / results.maxScore
        commRangeList = settings.commRangeList

        scoreList = scoreArray[0, :, :]
        avgScoreList = np.average(scoreList, axis=1)

        color = colorList[i]
        if plotPopulation:
            label = f"popSize={settings.mapSettings.creatureCount}"
        else:
            label = f"{settings.mapSettings.name}(R={settings.mapSettings.r1})"

        plt.plot(commRangeList, avgScoreList, label=label, color=color)
        plt.scatter(commRangeList, avgScoreList, color=color, s=12)

        maxScore = max(maxScore, np.amax(scoreList))
        xMax = max(xMax, np.amax(commRangeList))
        yMax = max(yMax, np.amax(avgScoreList))

    if useAUC:
        metric = "AUC"
    else:
        metric = "Score"

    if plotPopulation:
        plt.title(f"{metric} vs commRange with Tmax={settings.op.tMax}, R={settings.mapSettings.r1}")
    else:
        plt.title(f"{metric} vs commRange with Tmax={settings.op.tMax}, population={settings.mapSettings.creatureCount}")

    plt.xlim(0, xMax)
    plt.ylim(0, min(yMax * 1.1, 1))

    plt.xlabel("Maximum communication range")
    plt.ylabel("Average Score / max theoretical score")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend(fontsize=8)

    plt.show()

def plotNComm(settingsList, resultsList, colorList, useAUC=False):

    maxScore = 0
    xMax = 0
    yMax = 0
    for i in range(len(settingsList)):
        settings, results, color = settingsList[i], resultsList[i], colorList[i]
        nComm = settings.simSettings.nComm

        if useAUC:
            scoreArray = results.uacArray / results.maxUAC
        else:
            scoreArray = results.scoreArray / results.maxScore
        commRangeList = settings.commRangeList

        scoreList = scoreArray[0, :, :]
        avgScoreList = np.average(scoreList, axis=1)

        color = colorList[i]

        plt.plot(commRangeList, avgScoreList, label=f"nComm={nComm}", color=color)
        plt.scatter(commRangeList, avgScoreList, color=color, s=12)

        maxScore = max(maxScore, np.amax(scoreList))
        xMax = max(xMax, np.amax(commRangeList))
        yMax = max(yMax, np.amax(avgScoreList))

    if useAUC:
        metric = "AUC"
    else:
        metric = "Score"

    plt.title(f"{metric} vs commRange with Tmax={settings.op.tMax}, population={settings.mapSettings.creatureCount}, R={settings.mapSettings.r1}")

    plt.xlim(0, xMax)
    plt.ylim(0, min(yMax * 1.1, 1))

    plt.xlabel("Maximum communication range")
    plt.ylabel("Average Score / max theoretical score")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend(fontsize=8)

    plt.show()


def plotPComm(settingsList, resultsList, colorList, useAUC=False, plotPopulation=False, invertX=False):

    maxScore = 0
    xMax = 0
    yMax = 0
    for i in range(len(settingsList)):
        settings, results, color = settingsList[i], resultsList[i], colorList[i]

        if useAUC:
            scoreArray = results.uacArray / results.maxUAC
        else:
            scoreArray = results.scoreArray / results.maxScore
        pCommList = np.array([automata.pComm for automata in settings.automataList])

        scoreList = scoreArray[:, 0, :]
        avgScoreList = np.average(scoreList, axis=1)

        scoreMax = avgScoreList[pCommList > 100][0]
        scoreMin = avgScoreList[pCommList == 0][0]

        plt.axhline(scoreMin, linestyle="--", color="blue", label="No communication")
        plt.axhline(scoreMax, linestyle="--", color="green", label="Full communication")

        if invertX:
            avgScoreList = avgScoreList[pCommList != 0]
            pCommList = pCommList[pCommList != 0]
            pCommList = 1 / pCommList
        else:
            avgScoreList = avgScoreList[pCommList < 100]
            pCommList = pCommList[pCommList < 100]


        color = colorList[i]
        if plotPopulation:
            label = f"popSize={settings.mapSettings.creatureCount}"
        else:
            label = f"{settings.mapSettings.name}(R={settings.mapSettings.r1})"

        plt.plot(pCommList, avgScoreList, label=label, color=color)
        plt.scatter(pCommList, avgScoreList, color=color, s=12)

        maxScore = max(maxScore, np.amax(scoreList))
        xMax = max(xMax, np.amax(pCommList))
        yMax = max(yMax, np.amax(avgScoreList))

    if useAUC:
        metric = "AUC"
    else:
        metric = "Score"

    if plotPopulation:
        plt.title(f"{metric} vs p(comm) with Tmax={settings.op.tMax}, R={settings.mapSettings.r1}")
    else:
        plt.title(f"{metric} vs p(comm) with Tmax={settings.op.tMax}, population={settings.mapSettings.creatureCount}")

    plt.xlim(0, xMax)
    plt.ylim(0, min(yMax * 1.1, 1))

    if invertX:
        plt.xlabel("1 / p(communication)")
    else:
        plt.xlabel("p(communication)")
    plt.ylabel("Average Score / max theoretical score")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend(fontsize=8)

    plt.show()


def plotCommRangeOptimizerProgession(settings, results):


    parameterArray = results.parameterArray

    commRangeArray = np.array([[parameter.valueDict["commRange"] for parameter in parameterList] for parameterList in parameterArray])
    # plt.xticks(range(len(commRangeArray)))


    commRangeAvg = np.average(commRangeArray[3:,:])


    for i in range(commRangeArray.shape[1]):
        plt.scatter(range(len(commRangeArray)), commRangeArray[:,i], color="black",alpha=0.5)


    plt.yticks(range(int(np.amax(commRangeArray))+2))
    plt.xlim(-1, len(commRangeArray))
    plt.hlines(commRangeAvg, -10, len(commRangeArray), linestyle="--", color="red", label="average")
    plt.title(f"CommRange optimization for R={settings.mapSettings.r1}, popSize={settings.mapSettings.creatureCount}")

    plt.xlabel("Generation")
    plt.ylabel("Communication range")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend()

    plt.show()

def plotOptimalCommRange(settingsList, resultsList, nCut = 3, xPopSize=False):

    RList = []
    popSizeList = []
    commRangeList = []

    for i in range(len(settingsList)):

        settings, results = settingsList[i], resultsList[i]
        parameterArray = results.parameterArray

        commRangeArray = np.array(
            [[parameter.valueDict["commRange"] for parameter in parameterList] for parameterList in parameterArray])

        R, popSize = settings.mapSettings.r1, settings.mapSettings.creatureCount
        commRange = np.average(commRangeArray[3:, :])

        RList.append(R)
        popSizeList.append(popSize)
        commRangeList.append(commRange)

    RList, popSizeList, commRangeList = np.array(RList), np.array(popSizeList), np.array(commRangeList)

    if xPopSize:

        for R in np.unique(RList):
            cond = RList == R


            plt.plot(popSizeList[cond], commRangeList[cond], label=f"roomSize={R}")
            plt.scatter(popSizeList[cond], commRangeList[cond])

        plt.xlabel("Population Size")
    else:

        for popSize in np.unique(popSizeList):
            cond = popSizeList == popSize

            plt.plot(RList[cond], commRangeList[cond], label=f"popSize={popSize}")
            plt.scatter(RList[cond], commRangeList[cond])

        plt.xlabel("Room Size")

    plt.ylabel("Optimal Communication range")

    plt.legend()
    plt.grid(linestyle="--")
    plt.show()


def plotPDistort(settings, results, colorList, useAUC=False):

    maxScore = 0
    xMax = 0
    yMax = 0

    for i, simSettingsList in enumerate(settings.simSettingsArray):

        nComm = simSettingsList[0].nComm
        pDistortList = [simSettings.pDistortCoord for simSettings in simSettingsList]

        if useAUC:
            scoreArray = results.uacArray[:, i, :] / results.maxUACArray[i, :]
        else:
            scoreArray = results.scoreArray[:, i, :] / results.maxScoreArray[i, :]


        avgScoreList = np.average(scoreArray, axis=0)

        plt.plot(pDistortList, avgScoreList, label=f"nComm={nComm}", color=colorList[i])
        plt.scatter(pDistortList, avgScoreList, color=colorList[i], s=12)

        maxScore = max(maxScore, np.amax(avgScoreList))
        xMax = max(xMax, np.amax(pDistortList))
        yMax = max(yMax, np.amax(avgScoreList))

    if useAUC:
        metric = "AUC"
    else:
        metric = "Score"

    popSize = settings.mapSettingsArray[0].creatureCount
    r1 = settings.mapSettingsArray[0].r1
    plt.title(f"{metric} vs pDistortCoord with Tmax={settings.op.tMax}, population={popSize}, R={r1}")

    plt.xlim(0, xMax)
    plt.ylim(0, min(yMax * 1.1, 1))

    plt.xlabel("pDistort")
    plt.ylabel("Average Score / max theoretical score")

    plt.grid(linestyle="--", alpha=0.5)
    plt.legend(fontsize=8)

    plt.show()


def determineIfAntMill(waypointDistances, foodCollected, settings, minFoodIncrease, minWaypointDistance):

    def averageBackwards(xList, n):

        xAveraged = np.zeros(xList.shape)
        for i in range(xList.shape[1]):
            iMin = max(0, i - n+1)
            xAveraged[:, i] = np.average(xList[:, iMin:i+1], axis=1)

        return xAveraged

    def diff(xList):
        xDiff = np.diff(xList)
        return np.insert(xDiff, 0, 0,axis=1)

    popSize = settings.mapSettingsArray[0].creatureCount
    R = settings.mapSettingsArray[0].r1 + settings.mapSettingsArray[0].d
    walkDistance = 2 * R + 1
    nAverage = walkDistance

    foodCollectedArray = averageBackwards(foodCollected, nAverage) * nAverage
    foodIncreaseArray = diff(foodCollectedArray) / (nAverage * popSize / walkDistance)

    isAntMillArray = (foodIncreaseArray < minFoodIncrease) * (waypointDistances < minWaypointDistance) * (waypointDistances >= 0)
    return isAntMillArray


def plotAntMillFactors(settings, results, IncludeDistance1=True, IncludeDistance2=True, includeDistance3=True, includeAntMill=True):

    def average(x):
        coordSetList = np.sum(x >= 0, axis=0)
        coordSetList[coordSetList == 0] += 1
        return np.sum(x * (x >= 0), axis=0) / coordSetList


    simSettingsArray = settings.simSettingsArray
    R = settings.mapSettingsArray[0].r1 + settings.mapSettingsArray[0].d
    for i in range(len(simSettingsArray)):
        for j in range(len(simSettingsArray[i,:])):
            nComm = simSettingsArray[i, j].nComm
            pDistortCoord = simSettingsArray[i, j].pDistortCoord

            minFoodIncrease = 0.15
            minWaypointDistance = 0.8

            avgAgentCenterDistanceArray = results.avgAgentCenterDistanceArray[:, :, i, j] / R
            avgWaypointCenterDistanceArray = results.avgWaypointCenterDistanceArray[:, :, i, j] / R
            avgWaypointAgentDistanceArray = results.avgWaypointAgentDistanceArray[:, :, i, j] / R
            foodCollectedArray = results.foodOverTimeArray[:, :, i, j]

            isAntMillArray = determineIfAntMill(avgWaypointCenterDistanceArray, foodCollectedArray, settings, minFoodIncrease, minWaypointDistance)

            distanceArrays = [avgAgentCenterDistanceArray, avgWaypointCenterDistanceArray, avgWaypointAgentDistanceArray, isAntMillArray]
            distanceNames = ["avg Agent-Center distance", "avg Waypoint-Center distance", "avg Waypoint-Agent distance", "has ant mill"]
            colorList = ["red", "green", "blue", "orange", "purple", "cyan"]
            includedList = [IncludeDistance1, IncludeDistance2, includeDistance3, includeAntMill]

            tMax = settings.op.tMax

            for k in range(len(distanceArrays)):
                if not includedList[k]:
                    continue

                for distanceList in distanceArrays[k]:
                    pass
                    plt.plot(range(tMax), distanceList, color=colorList[k], alpha=0.1)

                plt.plot(range(tMax), average(distanceArrays[k]), color=colorList[k], label=distanceNames[k])


            r1 = settings.mapSettingsArray[0].r1
            plt.title(f"Ant mill formation for R={r1}, nComm={nComm},pDistort={pDistortCoord}")

            plt.xlim(0, tMax)
            # plt.ylim(0, 1.1)

            plt.xlabel("time(simulation ticks)")
            plt.ylabel("Average waypoint-center distance")

            plt.grid(linestyle="--", alpha=0.5)
            plt.legend(fontsize=8)

            plt.show()

def plotAntMillGraph(settings, results):

    green = np.array([122, 97, 80])
    red = [0, 97, 80]

    simSettingsArray = settings.simSettingsArray
    R = settings.mapSettingsArray[0].r1 + settings.mapSettingsArray[0].d
    maxNComm = 0
    maxpDistort = 0

    plt.axhline(0, color="black", linewidth=1, linestyle="--")
    plt.axvline(0, color="black", linewidth=1, linestyle="--")

    for i in range(len(simSettingsArray)):
        for j in range(len(simSettingsArray[i,:])):

            nComm = simSettingsArray[i, j].nComm
            pDistortCoord = simSettingsArray[i, j].pDistortCoord

            maxNComm = max(nComm, maxNComm)
            maxpDistort = max(pDistortCoord, maxpDistort)

            minFoodIncrease = 0.15
            minWaypointDistance = 0.8

            avgWaypointCenterDistanceArray = results.avgWaypointCenterDistanceArray[:, :, i, j] / R
            foodCollectedArray = results.foodOverTimeArray[:, :, i, j]

            isAntMillArray = determineIfAntMill(avgWaypointCenterDistanceArray, foodCollectedArray, settings, minFoodIncrease, minWaypointDistance)
            antMillRate = np.average(isAntMillArray[:, 2000:])

            color = green + (red - green) * antMillRate
            color = colorsys.hsv_to_rgb(color[0] / 359, color[1] / 100, color[2] / 100)

            plt.scatter(nComm, pDistortCoord, color=(color[0],color[1],color[2]))

    plt.xlabel("nComm")
    plt.ylabel("p(distort)")



    plt.xlim(-0.1, 1.2 * maxNComm)
    plt.ylim(-0.005, 1.2 * maxpDistort)

    plt.grid(linestyle="--", alpha=0.5)

    plt.show()



if __name__ == "__main__":

    if False:
        settingsArray, resultsArray = readResults()
        settings = settingsArray[0]
        results = resultsArray[0][0]

        scoreList = getRealScore(settings, results, 100)

        plotRealScore(scoreList)

        # plotScore(results)
        # plotSize(results)
        #
        # printBestAutomata(results)

    if False:
        settingsArray, resultsArray = readResults("PopExperiment")

        settings = settingsArray[2]
        results = resultsArray[2][0]

        plotPopScoreGraph(settings, results, ["Mute Agent", "Communicating Agent"])

    if False:

        settingsArray, resultsArray = readResults("CommRangeExperiment")

        settings = settingsArray[14]
        results = resultsArray[14][0]

        plotCommScoreGraphSingle(settings, results, "green")

    if False:

        indices = [11, 12, 13, 14, 15]

        settingsArray, resultsArray = readResults("CommRangeExperiment")

        settingsList = [settingsArray[i] for i in indices]
        resultsList = [resultsArray[i][0] for i in indices]
        colorList = ["red", "blue", "green", "orange", "purple"]

        plotCommScoreMultSizes(settingsList, resultsList, colorList, False)

    if False:

        indices = [14, 16, 17, 18]

        settingsArray, resultsArray = readResults("CommRangeExperiment")

        settingsList = [settingsArray[i] for i in indices]
        resultsList = [resultsArray[i][0] for i in indices]
        colorList = ["red", "blue", "green", "orange"]

        plotCommScoreMultSizes(settingsList, resultsList, colorList, True, True)

    if False:

        settingsArray, resultsArray = readResults("CommRangeOptimizer")

        index = 12
        settings = settingsArray[index]
        results = resultsArray[index][0]

        plotCommRangeOptimizerProgession(settings, results)

    if False:

        settingsArray, resultsArray = readResults("CommRangeOptimizer")

        indices = range(12, 31)
        settingsList = [settingsArray[i] for i in indices]
        resultsList = [resultsArray[i][0] for i in indices]

        plotOptimalCommRange(settingsList, resultsList, 3, True)

    if False:

        settingsArray, resultsArray = readResults("pCommExperiment")

        indices = [2]

        settingsList = [settingsArray[i] for i in indices]
        resultsList = [resultsArray[i][0] for i in indices]
        colorList = ["red"]

        plotPComm(settingsList, resultsList, colorList, False, True, False)

    if False:

        indices = list(range(14,20))

        settingsArray, resultsArray = readResults("nCommExperiment")

        settingsList = [settingsArray[i] for i in indices]
        resultsList = [resultsArray[i][0] for i in indices]
        colorList = ["red", "blue", "green", "orange", "purple", "darkgoldenrod","deepskyblue", "cyan"]

        plotNComm(settingsList, resultsList, colorList, True)

    if False:

        index = 3

        settingsArray, resultsArray = readResults("pDistort-nCommExperiment")
        settings, results = settingsArray[index], resultsArray[index][0]

        colorList = ["red", "blue", "green"]

        plotPDistort(settings, results, colorList, False)

    if True:

        index = 9

        settingsArray, resultsArray = readResults("pDistort-nCommExperiment")
        settings, results = settingsArray[index], resultsArray[index][0]

        plotAntMillFactors(settings, results, False, True, False, False)


    if False:

        index = 9

        settingsArray, resultsArray = readResults("pDistort-nCommExperiment")
        settings, results = settingsArray[index], resultsArray[index][0]

        plotAntMillGraph(settings, results)

