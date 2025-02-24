import argparse
import pandas as pd
from datetime import datetime, timedelta

def trace_back(file, time):
    df = pd.read_csv(file)
    # 读取_item_id和_hrn_stet列
    df = df[['_item_id', '_hrn_stet']]
    # 遍历_hrn_stet列的数据
    for hrn_stet in df['_hrn_stet']:
        prefix = hrn_stet.strip().split('/')[0] + '/'
        suffix = '-' + hrn_stet.strip().split('/')[-1].split('-')[-1]

        start_time = hrn_stet.strip().split('/')[-1].split('-')[0]

        ms = start_time.split('_')[-1]
        start_time_no_ms = start_time.split('_')[0]+'_'+start_time.split('_')[1]
        start_time_no_ms = datetime.strptime(start_time_no_ms, '%Y%m%d_%H%M%S')

        start_time_no_ms = start_time_no_ms - timedelta(seconds=int(time))

        new_start_time = start_time_no_ms.strftime('%Y%m%d_%H%M%S') + '_' + ms

        new_hrn = prefix + new_start_time + suffix

        # 将new_hrn替换到df中
        df.loc[df['_hrn_stet'] == hrn_stet, '_hrn_stet'] = new_hrn

    file_name = file.split('.')[0] + '_' + time + '.csv'

    # 将df写入csv文件
    df.to_csv(file_name, index=False)

def parse_args():
    parser = argparse.ArgumentParser(description='前摇hrn切片时间')
    parser.add_argument('--input', type=str, required=True, help='输入文件路径')
    parser.add_argument('--time', type=str, required=True, help='前摇hrn切片时间')
    return parser.parse_args()


def main():
    args = parse_args()
    file = args.input
    time = args.time

    trace_back(file, time)


if __name__ == '__main__':
    main()
