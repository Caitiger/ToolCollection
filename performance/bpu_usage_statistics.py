import fire
import statistic_utils

from draw_chart import draw_line_chart


def count_bpu_usage(log_file):
    num = 0

    chart_x = []
    data_list = []

    with open(log_file, "r") as log_f:
        for line in log_f.readlines():
            bpu_use = float(line)
            num += 1

            data_list.append(bpu_use)
            chart_x.append(num * 10 / 1000 / 60)

    # avg = sum_usage / num
    print("=================BPU Usage=================")
    statistic_utils.show_max_min_avg(data_list)
    print("=================3 Sigma=================")
    statistic_utils.show_three_sigma(data_list)

    draw_line_chart(data_list, chart_x, "bpu(%)", "time(min)")


if __name__ == "__main__":
    fire.Fire(count_bpu_usage)
