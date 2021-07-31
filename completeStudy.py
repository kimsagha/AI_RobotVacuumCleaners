from vacuumingExperiment import *
import pandas as pd
import matplotlib.pyplot as plt
import random
from scipy.stats import ttest_ind
import openpyxl


def run_set_of_experiments(number_of_runs):
    # initialise a seeded list of random seeds, one for each run (to be able to reproduce the results)
    random.seed(100)
    mySeeds = random.sample(range(1, 1000), number_of_runs)

    # initialise the results table
    resultsTable = {}

    # initialise the columns of the results table, one for each parameter configuration
    # T: true, F: false
    # First parameter: battery, second parameter: bin
    dirtCollectedWanderingTT = []
    dirtCollectedWanderingFT = []
    dirtCollectedWanderingTF = []
    dirtCollectedWanderingFF = []

    dirtCollectedPlanningTT = []
    dirtCollectedPlanningFT = []
    dirtCollectedPlanningTF = []
    dirtCollectedPlanningFF = []

    # for each configuration of parameters, run a set of number_of_runs experiments, with a new seed for each experiment
    # pass the following parameters to each experiment:
    #   - strategy (wandering or planning)
    #   - battery_usage (true or false)
    #   - dirt_bin_usage (true or false)
    #   - seed: determines dirt distribution, wandering movement, etc.
    for i in range(number_of_runs):
        dirtCollectedWanderingTT.append(run_one_experiment("wandering", True, True, mySeeds[i]))
        dirtCollectedWanderingFT.append(run_one_experiment("wandering", False, True, mySeeds[i]))
        dirtCollectedWanderingTF.append(run_one_experiment("wandering", True, False, mySeeds[i]))
        dirtCollectedWanderingFF.append(run_one_experiment("wandering", False, False, mySeeds[i]))

        dirtCollectedPlanningTT.append(run_one_experiment("planning", True, True, mySeeds[i]))
        dirtCollectedPlanningFT.append(run_one_experiment("planning", False, True, mySeeds[i]))
        dirtCollectedPlanningTF.append(run_one_experiment("planning", True, False, mySeeds[i]))
        dirtCollectedPlanningFF.append(run_one_experiment("planning", False, False, mySeeds[i]))

    # add the columns of data (results from the experiments) to the results table with relevant column names
    resultsTable["wandering,T,T"] = dirtCollectedWanderingTT
    resultsTable["wandering,F,T"] = dirtCollectedWanderingFT
    resultsTable["wandering,T,F"] = dirtCollectedWanderingTF
    resultsTable["wandering,F,F"] = dirtCollectedWanderingFF

    resultsTable["planning,T,T"] = dirtCollectedPlanningTT
    resultsTable["planning,F,T"] = dirtCollectedPlanningFT
    resultsTable["planning,T,F"] = dirtCollectedPlanningTF
    resultsTable["planning,F,F"] = dirtCollectedPlanningFF

    # convert final results table to a DataFrame
    results = pd.DataFrame(resultsTable)

    # print the first few rows of all 8 columns of the DataFrame for checking
    pd.set_option('display.max_columns', None)
    print(results.head(10))

    # return results from this set of experiments
    return results


def visualise_experimental_results(number_of_runs):
    # run set of experiments with a given number of runs
    results = run_set_of_experiments(number_of_runs)

    # write results to an excel file (to later be able to read in the file to
    # reformat/visualise the data without having to re-run the experiments)
    results.to_excel("data.xlsx")

    # obtain previous results from excel file (if not running a new set of experiments)
    # results = pd.read_excel('data.xlsx')
    # results = results.drop(results.columns[0], axis=1)  # delete column of indices
    # print the first few rows of the results for checking
    # pd.set_option('display.max_columns', None)
    # print(results.head(10))

    # perform t-test
    # t-test t-statistics comparing wandering with planning bots for all 4 parameter-configurations
    tt_t_value = ttest_ind(results["wandering,T,T"], results["planning,T,T"])[0]
    ft_t_value = ttest_ind(results["wandering,F,T"], results["planning,F,T"])[0]
    tf_t_value = ttest_ind(results["wandering,T,F"], results["planning,T,F"])[0]
    ff_t_value = ttest_ind(results["wandering,F,F"], results["planning,F,F"])[0]
    t_values = [tt_t_value, ft_t_value, tf_t_value, ff_t_value]
    t_values = [abs(val) for val in t_values]  # get absolute t-values

    # t-test p-values comparing wandering with planning bots for all 4 parameter-configurations
    tt_p_value = ttest_ind(results["wandering,T,T"], results["planning,T,T"])[1]
    ft_p_value = ttest_ind(results["wandering,F,T"], results["planning,F,T"])[1]
    tf_p_value = ttest_ind(results["wandering,T,F"], results["planning,T,F"])[1]
    ff_p_value = ttest_ind(results["wandering,F,F"], results["planning,F,F"])[1]
    p_values = [tt_p_value, ft_p_value, tf_p_value, ff_p_value]

    # plot results of t-test in a grouped bar chart
    x = np.arange(4)
    plt.bar(x - 0.2, t_values, 0.4)
    for i in range(4):
        plt.annotate(round(t_values[i], 1), xy=(i, t_values[i]), xytext=(i-0.3, t_values[i]+0.02))
    plt.bar(x + 0.2, p_values, 0.4)
    for i in range(4):
        plt.annotate(round(p_values[i], 2), xy=(i, p_values[i]), xytext=(i, p_values[i]+0.02))
    plt.title("T-test results comparing wandering with planning bots in all experiments")
    plt.xlabel('Experimental setup (battery, bin)')
    plt.xticks(x, ["T,T", "F,T", "T,F", "F,F"])
    plt.legend(['t-value', 'p-value'])
    plt.show()

    # show a box plot to see the distribution of data points for the runs of each experiment
    results.boxplot(grid=False)
    plt.title("Distribution of results in all experiments")
    plt.xlabel('Experimental setup (strategy, battery, bin)')
    plt.ylabel('Dirt collected')
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8], ["w,T,T", "w,F,T", "w,T,F", "w,F,F", "p,T,T", "p,F,T", "p,T,F", "p,F,F"])
    plt.show()

    # show a bar chart with the mean values of each parameter-configuration
    col_names = np.array(["w,T,T", "w,F,T", "w,T,F", "w,F,F",
                          "p,T,T", "p,F,T", "p,T,F", "p,F,F"])
    means = results.mean(axis=0).values.tolist()
    col_means = np.array(means)
    plt.bar(col_names, col_means)
    for i in range(8):
        plt.annotate(round(col_means[i], 1), xy=(i, col_means[i]), xytext=(i-0.3, col_means[i]+0.1))
    plt.title("Mean values of all experiments, each with 40 different dirt distributions")
    plt.xlabel('Experimental setup (strategy, battery, bin)')
    plt.ylabel('Mean of dirt collected')
    plt.show()


# input number of runs for each experiment
# determines how many different random distributions of dirt to test for each parameter configuration
visualise_experimental_results(70)
