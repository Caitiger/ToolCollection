import fire

import statistic_utils
from draw_chart import draw_line_chart


def count_cpu_usage(log_file, key_word):
    num = 0

    chart_x = []
    data_list = []

    with open(log_file, "r") as log_f:
        for line in log_f.readlines():
            if key_word in line:
                cpu_use = float(line.strip().split()[-5])
                num += 1

                data_list.append(cpu_use)
                chart_x.append(num * 10 / 1000 / 60)

    print("=================CPU Usage=================")
    statistic_utils.show_max_min_avg(data_list)
    print("=================3 Sigma=================")
    statistic_utils.show_three_sigma(data_list)

    draw_line_chart(data_list, chart_x, "cpu(%)", "time(min)")


if __name__ == "__main__":
    fire.Fire(count_cpu_usage)
