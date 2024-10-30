
#-----Imports-----#
import concurrent.futures
import numpy as np

def runAsync(func, nRuns, args=[], maxSize=16):

    resultsList = np.empty(nRuns, dtype=list)

    runsLeft = nRuns

    while runsLeft > 0:

        if runsLeft > maxSize:
            currentRuns = maxSize
            runsLeft -= maxSize
        else:
            currentRuns = runsLeft
            runsLeft = 0

        with concurrent.futures.ProcessPoolExecutor() as executor:

            futures = [executor.submit(func, i, *args) for i in range(currentRuns)]

            for future in concurrent.futures.as_completed(futures):
                try:
                     i, results = future.result()
                     resultsList[i + runsLeft] = results

                except Exception as exc:
                    print(f"Simulation generated an exception: {exc}")

    return resultsList