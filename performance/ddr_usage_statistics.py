import fire
import statistic_utils
from draw_chart import draw_line_chart


def count_avg(line_list):
    num = 0

    chart_x = []
    data_list = []

    for line in line_list:
        usage = line.strip().split("|")
        if usage[-1] != '':
            ddr_use = float(usage[-1])
            num += 1

            data_list.append(ddr_use)
            chart_x.append(num * 10 / 1000 / 60)

    statistic_utils.show_max_min_avg(data_list)
    print("=================3 Sigma=================")
    statistic_utils.show_three_sigma(data_list)

    draw_line_chart(data_list, chart_x, "bandwidth(MB/s)", "time(min)")


def count_ddr_usage(log_file):
    read_ddr_line = []
    write_ddr_line = []

    with open(log_file, "r") as log_f:
        for line in log_f.readlines():
            line = line.strip()
            if "Read" in line:
                read_ddr_line.append(line)
            elif "Write" in line:
                write_ddr_line.append(line)

    print("=================Read ddr width=================")
    count_avg(read_ddr_line)

    print("=================Write ddr width=================")
    count_avg(write_ddr_line)


if __name__ == "__main__":
    fire.Fire(count_ddr_usage)
