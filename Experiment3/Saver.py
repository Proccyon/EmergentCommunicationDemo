
#-----Imports-----#
import os
import pickle
import numpy as np

class Log:

    def __init__(self):
        self.current = []
        self.log = []

    def add(self, x):
        self.current.append(x)

    def finish(self):

        if len(self.current) > 0:
            xAvg = np.average(self.current)
        else:
            xAvg = 0

        self.log.append(xAvg)
        self.current = []

    def pastAverage(self, window):

        n = len(self.log)

        if window > n:
            return np.average(self.log)
        else:
            return np.average(self.log[n-window:n])


# Saves results of simulation to a folder
# If a simulation was already run and saved with same settings as current
# -> save sim in same folder
# Otherwise create new folder
def save(settings, results):

    folderName = "SimResults"
    i = 1

    while True:

        path = folderName + str(i)

        # If folder doesn't exist we have looped through all folders and create a new one
        if not os.path.isdir(path):
            return saveNewDir(path, settings, results)

        # Load settings of currently examined folder
        with open(path + "/pickledSettings.obj", 'rb') as settingsFile:
            folderSettings = pickle.load(settingsFile)

        # If settings are same as our settings save results there
        if folderSettings == settings:
            return saveOldDir(path, results)

        #Else check the next folder
        else:
            i += 1


# Creates a new folder for results with given simulation settings and save results there
def saveNewDir(path, settings, results):

    os.makedirs(path)

    with open(path + "/pickledSettings.obj", 'wb') as settingsFile:
        pickle.dump(settings, settingsFile)

    saveRun(path+"/Run1", results)


# Save results to an already existing folder
def saveOldDir(path, results):

    i = 1
    while True:

        runPath = path + "/Run" + str(i)

        if os.path.isdir(runPath):
            i += 1
        else:
            return saveRun(runPath, results)


def saveRun(path, results):

    os.makedirs(path)

    with open(f"{path}/PickledResults.obj", "wb") as pickledResultsFile:
        pickle.dump(results, pickledResultsFile)





