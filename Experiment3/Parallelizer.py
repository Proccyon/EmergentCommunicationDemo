
#-----Imports-----#
import concurrent.futures


def runAsync(func, nRuns, args=[]):

    resultsList = []

    with concurrent.futures.ProcessPoolExecutor() as executor:

        futures = [executor.submit(func, i, *args) for i in range(nRuns)]

        for future in concurrent.futures.as_completed(futures):
            try:
                 results = future.result()
                 resultsList.append(results)

            except Exception as exc:
                print(f"Simulation generated an exception: {exc}")

    return resultsList