import argparse
from datetime import datetime, timedelta

HRN_PREFIX = 'hrn:GA20230001:clip:'


def parse_args():
    parser = argparse.ArgumentParser(description='生成hrn文件')
    parser.add_argument('--car', type=str, required=True, help='车辆')
    # parser.add_argument('--start', type=str, required=True,
    #                     help='开始时间,格式: 2025-01-04 15:35:25')
    # parser.add_argument('--end', type=str, required=True,
    #                     help='结束时间,格式: 2025-01-04 16:52:39')
    parser.add_argument('--hrn_info_file', type=str, required=True,
                        help='hrn信息文件')
    parser.add_argument('--output_file', type=str, required=True,
                        help='输出文件')
    return parser.parse_args()


def gen_hrn(car, hrn_info, output_file):
    task_id, start, end = hrn_info

    title = f">>>>>>>>>>>>>>>>>>>>>>>>gen hrn for {car}-{task_id}<<<<<<<<<<<<<<<<<<<<<<<<<"

    # 将字符串转换为datetime对象
    start_time = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')

    hrn_for_aidi = ""
    hrn_for_sheet = ""
    # 以10分钟为间隔进行切分
    current_time = start_time
    while current_time < end_time:
        next_time = current_time + timedelta(minutes=10)
        if next_time > end_time:
            next_time = end_time

        # 获取毫秒部分并保留三位数
        current_millis = current_time.strftime('%f')[:3]
        next_millis = next_time.strftime('%f')[:3]

        hrn_item = f"{HRN_PREFIX}{car}/" \
            f"{current_time.strftime('%Y%m%d_%H%M%S')}_{current_millis}-" \
            f"{next_time.strftime('%Y%m%d_%H%M%S')}_{next_millis}"

        hrn_for_aidi += f"{hrn_item}"
        hrn_for_sheet += f"{hrn_item}"

        if next_time != end_time:
            hrn_for_aidi += ","
            hrn_for_sheet += "\n"

        current_time = next_time

    # print(f"=============================copy for sheet:=============================")
    # print(hrn_for_sheet)
    # print(f"=============================copy for aidi:=============================")
    # print(hrn_for_aidi)

    with open(output_file, 'a') as file:
        file.write(title + '\n')
        file.write("=============================copy for sheet:=============================\n")
        file.write(hrn_for_sheet + '\n')
        file.write("=============================copy for aidi:=============================\n")
        file.write(hrn_for_aidi + '\n')
        file.write("\n")  # Add a newline for separation between entries

def read_time_from_file(file_path):
    hrn_info_list = []
    with open(file_path, 'r') as file:
        for line in file:
            line_id, start, end = line.strip().split('~')
            hrn_info_list.append((line_id, start.strip(), end.strip()))
    return hrn_info_list

if __name__ == '__main__':
    args = parse_args()

    hrn_info_list = read_time_from_file(args.hrn_info_file)
    for hrn_info in hrn_info_list:
        gen_hrn(args.car, hrn_info, args.output_file)
