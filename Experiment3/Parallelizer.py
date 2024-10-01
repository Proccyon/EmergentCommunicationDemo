
#-----Imports-----#
import concurrent.futures
import numpy as np

def runAsync(func, nRuns, args=[]):

    resultsList = np.empty(nRuns)

    with concurrent.futures.ProcessPoolExecutor() as executor:

        futures = [executor.submit(func, i, *args) for i in range(nRuns)]

        for future in concurrent.futures.as_completed(futures):
            try:
                 i, results = future.result()
                 resultsList[i] = results

            except Exception as exc:
                print(f"Simulation generated an exception: {exc}")

    return resultsList