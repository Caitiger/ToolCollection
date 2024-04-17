import numpy as np


def show_three_sigma(data_list):
    mean = np.mean(data_list)
    std_dev = np.std(data_list)

    print(f"mean is {mean:.2f}, std_dev is {std_dev:.2f}")

    lower_bond = mean - 3 * std_dev
    upper_bond = mean + 3 * std_dev

    print(f"3sigma lower_bond is {lower_bond:.2f}, upper_bond is {upper_bond:.2f}")


def show_max_min_avg(data_list):
    max_data = np.max(data_list)
    min_data = np.min(data_list)
    avg_data = np.average(data_list)

    print(f"max_usage is {max_data:.2f}, min_usage is {min_data:.2f}, avg is {avg_data:.2f}")
