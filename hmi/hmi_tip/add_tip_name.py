import argparse
from ruamel.yaml import YAML


def add_tip_name(yaml_file, csv_file, output_file):
    # 初始化YAML解析器，保持顺序
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    # 读取yaml文件
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.load(f)

    # csv文件
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_data = f.readlines()

    # 遍历yaml文件中的hmi_tips数组
    for tip in yaml_data['hmi_tips']:
        # 从proto文件中查找tip_name
        if '0' == str(tip['tip_id']):
            tip['tip_name'] = 'TIP_ID_NONE'
        else:
            for line in csv_data:
                if 'TIP_ID_' in line and str(tip['tip_id']) in line:
                    print(str(tip['tip_id']))
                    print(line)
                    tip['tip_name'] = line.strip().split(',')[1].strip()
                    break

    # 写入新的yaml文件，保持原始顺序
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f)


def parse_args():
    parser = argparse.ArgumentParser(description='为yaml文件添加tip_name文件添加tip_name')
    parser.add_argument('--yaml', type=str, required=True, help='yaml文件路径')
    parser.add_argument('--csv', type=str, required=True, help='csv文件路径')
    parser.add_argument('--output', type=str, required=True, help='输出文件路径')
    return parser.parse_args()

def main():
    args = parse_args()
    yaml_file = args.yaml
    csv_file = args.csv
    output_file = args.output

    add_tip_name(yaml_file, csv_file, output_file)

if __name__ == '__main__':
    main()

