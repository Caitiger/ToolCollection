from datetime import date
import argparse

def days_between(date_1, date_2):
    """
    计算两个日期之间的天数差（考虑跨年和闰年）

    参数：
        year1, month1, day1 (int): 第一个日期的年、月、日
        year2, month2, day2 (int): 第二个日期的年、月、日

    返回：
        int: 两个日期之间的绝对天数差
    """
    year1 = int(date_1[0])
    month1 = int(date_1[1])
    day1 = int(date_1[2])

    year2 = int(date_2[0])
    month2 = int(date_2[1])
    day2 = int(date_2[2])

    d1 = date(year1, month1, day1)
    d2 = date(year2, month2, day2)
    delta = d2 - d1
    return abs(delta.days) + 1

def parse_args():
    parser = argparse.ArgumentParser(description="计算任意两天时间差")
    parser.add_argument('--d1', type=str, required=True, help='year.month.day')
    parser.add_argument('--d2', type=str, required=True, help='year.month.day')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    d_1 = args.d1.strip().split('.')
    d_2 = args.d2.strip().split('.')

    print(days_between(d_1, d_2))
