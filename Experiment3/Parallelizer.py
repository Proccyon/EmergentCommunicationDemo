
#-----Imports-----#
import concurrent.futures


def runAsync(func, nRuns):

    settingsList = []
    resultsList = []

    with concurrent.futures.ProcessPoolExecutor() as executor:

        futures = [executor.submit(func, i) for i in range(nRuns)]

        for future in concurrent.futures.as_completed(futures):
            try:
                settings, results = future.result()

                settingsList.append(settings)
                resultsList.append(results)

            except Exception as exc:
                print(f"Simulation generated an exception: {exc}")

    return settingsList, resultsList