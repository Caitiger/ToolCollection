import argparse

import pandas as pd
from ruamel.yaml import YAML
from googletrans import Translator

# 持续发送帧率
CONTINUOUS_PUB_COUNT = 10

SHEET_NAME_DRIVING_TIPS = "行车告警提示"
SHEET_NAME_FAULT_TIPS = "智驾故障报警及工程类提示"
SHEET_NAME_DRIVING_PRIORITY = "附_智驾意图提示优先级排序"
SHEET_NAME_CENTER_TIPS = "中控屏提示"
SHEET_NAME_VERSION = "版本"

# 未定义显示策略
TIPS_DISPLAY_UNDEFINE = 0
# 显示5s后自动结束
TIPS_DISPLAY_5_SECONDS = 1
# 随信号持续显示
TIPS_DISPLAY_WITH_SIGNAL = 2
# 随信号显示至少5s
TIPS_DISPLAY_WITH_SIGNAL_LEAST_5_SECONDS = 3

TIPS_DISPLAY_5_SECONDS_DESC = "5s"
TIPS_DISPLAY_WITH_SIGNAL_DESC = "随信号持续显示"
TIPS_DISPLAY_WITH_SIGNAL_LEAST_5_SECONDS_DESC = "随信号至少5s"

# 未定义告警消息
TIP_TYPE_UNDEFINE = 0
# 状态迁移告警消息
TIP_TYPE_STATE_TRANS = 1
# 激活失败告警消息
TIP_TYPE_ACTIVE_FAILED = 2
# 智驾内提示告警消息
TIP_TYPE_INTELLIGENT_DRIVING = 3
# 用户交互告警消息
TIP_TYPE_USER_INTERACTION = 4
# 主动安全告警消息
TIP_TYPE_ACTIVE_SAFETY = 5
# 智驾意图告警消息
TIP_TYPE_DRIVING_INTENT = 6
# 座舱故障提示告警
TIP_TYPE_IVI_FAULT = 7
# Beta工程类提示 (原故障告警)
TIP_TYPE_BETA_ENGINEER = 8


# 未定义显示区域
TIP_LOCATION_UNDEFINE = 0
# 仪表显示
TIP_LOCATION_METER = 1
# 灵动岛显示
TIP_LOCATION_ISLAND = 2
# 通知横幅显示
TIP_LOCATION_BANNER = 3


def parse_sheet(sheet):
    # 将返回类型从字典改为列表
    result_list = []

    # 遍历每一行
    for idx, row in sheet.iterrows():
        if pd.notna(row).any():  # 检查行中是否有非空值
            # 创建一个字典存储当前行的数据
            row_dict = {}
            # 遍历每一列
            for col in sheet.columns:
                value = row[col]
                # if pd.notna(value) and str(value).strip():
                row_dict[col.split('\n')[0]] = value
            result_list.append(row_dict)

    return result_list


def parse_subpri_sheet(sheet):
    result_dict = {}

    # 遍历每一列
    # 每3列为一组进行处理
    for i in range(0, len(sheet.columns), 3):
        if i + 2 >= len(sheet.columns):
            break

        # 获取第1列的值并进行映射
        keys = sheet[sheet.columns[i + 1]].iloc[:].dropna()
        # 将values转换为字符串并格式化小数点后的数字
        values = sheet[sheet.columns[i]]

        for j in range(0, len(values)):
            if pd.notna(values[j]) and str(values[j]).strip():
                try:
                    pre_num = values[j].split('.')[0]
                    last_num = values[j].split('.')[-1]

                    mapped_value = int(pre_num) * 100 + int(last_num)
                    result_dict[int(keys[j])] = mapped_value
                except ValueError:
                    continue

    return result_dict


def parse_xlsx(input_file, sheet_names):
    result_dict = {}

    for sheet_name in sheet_names:
        # 读取Excel文件中的指定sheet
        read_sheet = pd.read_excel(input_file, sheet_name=sheet_name, dtype=str)

        if SHEET_NAME_DRIVING_PRIORITY == sheet_name:
            # 解析"附：智驾意图提示优先级排序"sheet，获取子优先级
            result_dict[sheet_name] = parse_subpri_sheet(read_sheet)
        else:
            # 解析"**告警提示"sheet
            result_dict[sheet_name] = parse_sheet(read_sheet)

    return result_dict


def parse_args():
    parser = argparse.ArgumentParser(description='转换xlsx文件')
    parser.add_argument('--input', type=str, required=True, help='输入文件路径')
    parser.add_argument('--output', type=str, required=True, help='输出文件路径')
    return parser.parse_args()


def get_id_key(x):
    for k in x.keys():
        if 'ID' in k.upper():
            return k
    return None


def get_tip_type(id):
    tip_type = TIP_TYPE_UNDEFINE

    if id >= 10001 and id <= 10500:
        tip_type = TIP_TYPE_STATE_TRANS
    elif id >= 10501 and id <= 10750:
        tip_type = TIP_TYPE_ACTIVE_FAILED
    elif id >= 11001 and id <= 12000:
        tip_type = TIP_TYPE_INTELLIGENT_DRIVING
    elif id >= 12001 and id <= 13000:
        tip_type = TIP_TYPE_USER_INTERACTION
    elif id >= 13001 and id <= 13100:
        tip_type = TIP_TYPE_ACTIVE_SAFETY
    elif id >= 20001 and id <= 30000:
        tip_type = TIP_TYPE_DRIVING_INTENT
    elif id >= 30001 and id <= 40000:
        tip_type = TIP_TYPE_IVI_FAULT
    elif id >= 40001 and id <= 50000:
        tip_type = TIP_TYPE_BETA_ENGINEER

    return tip_type


def get_tip_display(display_desc):
    tip_display = TIPS_DISPLAY_UNDEFINE

    if display_desc == TIPS_DISPLAY_5_SECONDS_DESC:
        tip_display = TIPS_DISPLAY_5_SECONDS
    elif display_desc == TIPS_DISPLAY_WITH_SIGNAL_DESC:
        tip_display = TIPS_DISPLAY_WITH_SIGNAL
    elif display_desc == TIPS_DISPLAY_WITH_SIGNAL_LEAST_5_SECONDS_DESC:
        tip_display = TIPS_DISPLAY_WITH_SIGNAL_LEAST_5_SECONDS

    return tip_display


def get_tip_location(tip_type):
    tip_location = []

    if tip_type == TIP_TYPE_DRIVING_INTENT:
        tip_location.append(TIP_LOCATION_ISLAND)

    if tip_type == TIP_TYPE_BETA_ENGINEER:
        tip_location.append(TIP_LOCATION_BANNER)

    if tip_type != TIP_TYPE_DRIVING_INTENT:
        tip_location.append(TIP_LOCATION_METER)

    if len(tip_location) == 0:
        tip_location.append(TIP_LOCATION_UNDEFINE)

    return tip_location


def generate_yaml_file(xlsx_content, yaml_file):
    version = xlsx_content[SHEET_NAME_VERSION]

    latest_version = 0.0

    for item in version:
        if pd.notna(item.get('版本号')):
            version = float(item.get('版本号'))
            if version > latest_version:
                latest_version = version


    # 合并所有sheet的数据
    merged_list = []

    for key in [SHEET_NAME_DRIVING_TIPS, SHEET_NAME_FAULT_TIPS]:
        if key in xlsx_content:
            merged_list = merged_list + xlsx_content[key]

    # 按id值升序排序
    sorted_list = sorted(merged_list, key=lambda x: float(x[get_id_key(x)]))

    # 创建要写入的格式
    formatted_list = []

    formatted_item_none = {
        'tip_id': 0,
        'tip_state': "ON",
        'tip_type': 0,
        'tip_priority': 9999,
        'tip_sub_pri': 0,
        'tip_display': 0,
        'tip_desc': "tip_none",
        'tip_location': [],
        'tip_extend_1': [],
        'tip_extend_2': []
    }

    formatted_list.append(formatted_item_none)

    for item in sorted_list:
        if pd.notna(item.get('ID')):
            tip_id = int(item.get('ID'))

            level_str = item.get('等级')
            if level_str is None:
                level_str = item.get('Toast等级')

            if "Level" in level_str:
                tip_priority = int(level_str.split(' ')[-1])
            else:
                tip_priority = 9999

            tip_sub_pri = 0
            if tip_priority == 5:
                tip_sub_pri = xlsx_content[SHEET_NAME_DRIVING_PRIORITY].get(tip_id)

            tip_type = get_tip_type(tip_id)


            display_desc = item.get('显示策略')
            if display_desc is None:
                display_desc = item.get('Toast显示策略')

            tip_extend_1 = []
            if pd.notna(item.get('拓展字段1')) and item.get('拓展字段1') != '/':
                extend_1_list = item.get('拓展字段1').split('\n')
                if len(extend_1_list) > 1:
                    for extend_1 in extend_1_list:
                        tip_extend_1.append(extend_1.split(':')[-1])
                else:
                    tip_extend_1 = extend_1_list

            tip_extend_2 = []
            if pd.notna(item.get('拓展字段2')) and item.get('拓展字段2') != '/':
                extend_2_list = item.get('拓展字段2').split('\n')
                if len(extend_2_list) > 1:
                    for extend_2 in extend_2_list:
                        tip_extend_2.append(extend_2.split(':')[-1])
                else:
                    tip_extend_2 = extend_2_list

            tip_desc = ""
            if pd.notna(item.get('场景')):
                tip_desc = item.get('场景').split('\n')[0].strip().replace(' ', '')

            formatted_item = {
                'tip_id': tip_id,
                'tip_state': "ON",
                'tip_type': tip_type,
                'tip_priority': tip_priority,
                'tip_sub_pri': tip_sub_pri,
                'tip_display': get_tip_display(display_desc),
                'tip_desc': tip_desc,
                'tip_location': get_tip_location(tip_type),
                'tip_extend_1': tip_extend_1,
                'tip_extend_2': tip_extend_2
            }
            formatted_list.append(formatted_item)

    # 写入yaml文件
    output_data = {
        'version': latest_version,
        'continuous_pub_count': CONTINUOUS_PUB_COUNT,
        'hmi_tips': formatted_list}
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 1  # 强制每个键值对单独成行
    yaml.sequence_dash_offset = 2  # 设置破折号的缩进
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(output_data, f)


def generate_msg_prefix(xlsx_content, msg_prefix_file):
    msg_list = xlsx_content[SHEET_NAME_DRIVING_TIPS]

    # 按id值升序排序
    sorted_list = sorted(msg_list, key=lambda x: float(x[get_id_key(x)]))

    translator = Translator()

    msg_prefix_list = []
    for item in sorted_list:
        if pd.notna(item.get('ID')):
            msg_item = []
            tip_id = int(item.get('ID'))
            msg_item.append(tip_id)

            tip_desc = item.get('场景').split('\n')[0]
            translated_tip_desc = translator.translate(tip_desc, dest='en').text.upper().replace(' ', '_')

            print(translated_tip_desc)
            msg_item.append(translated_tip_desc)
            msg_item.append(tip_desc)

            msg_prefix_list.append(msg_item)

    # 写入文件
    with open(msg_prefix_file, 'w', encoding='utf-8') as f:
        for msg_prefix in msg_prefix_list:
            f.write(f"# {msg_prefix[2]}\n")
            f.write(f"int32 TIP_ID_{msg_prefix[1]} = {msg_prefix[0]}\n")


def convert_xlsx(input_file, output_path):
    sheet_names = [SHEET_NAME_VERSION,
                   SHEET_NAME_DRIVING_TIPS,
                #    SHEET_NAME_FAULT_TIPS,
                   SHEET_NAME_DRIVING_PRIORITY]

    xlsx_content = parse_xlsx(input_file, sheet_names)

    yaml_file = output_path + "/driving_tips_no_tip_name.yaml"
    generate_yaml_file(xlsx_content, yaml_file)

    # msg_prefix_file = output_path + "/msg_prefix.msg"
    # generate_msg_prefix(xlsx_content, msg_prefix_file)


if __name__ == '__main__':
    args = parse_args()
    input_file = args.input
    output_path = args.output

    convert_xlsx(input_file, output_path)
