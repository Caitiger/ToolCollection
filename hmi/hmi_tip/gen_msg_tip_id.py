import argparse

# 未定义告警消息
TIP_TYPE_UNDEFINE = 0
TIP_TYPE_UNDEFINE_STR = "# ----------------------无信号---------------------"
# 状态迁移告警消息
TIP_TYPE_STATE_TRANS = 1
TIP_TYPE_STATE_TRANS_STR = "# ----------------------状态迁移类告警---------------------"
# 激活失败告警消息
TIP_TYPE_ACTIVE_FAILED = 2
TIP_TYPE_ACTIVE_FAILED_STR = "# ----------------------激活失败类告警---------------------"
# 智驾内提示告警消息
TIP_TYPE_INTELLIGENT_DRIVING = 3
TIP_TYPE_INTELLIGENT_DRIVING_STR = "# ----------------------智驾内提示告警---------------------"
# 用户交互告警消息
TIP_TYPE_USER_INTERACTION = 4
TIP_TYPE_USER_INTERACTION_STR = "# ----------------------用户交互类告警---------------------"
# 主动安全告警消息
TIP_TYPE_ACTIVE_SAFETY = 5
TIP_TYPE_ACTIVE_SAFETY_STR = "# ----------------------主动安全类告警---------------------"
# 智驾意图告警消息
TIP_TYPE_DRIVING_INTENT = 6
TIP_TYPE_DRIVING_INTENT_STR = "# ----------------------智驾意图类告警---------------------"
# 座舱故障提示告警
TIP_TYPE_IVI_FAULT = 7
TIP_TYPE_IVI_FAULT_STR = "# ----------------------座舱故障---------------------"
# Beta工程类提示 (原故障告警)
TIP_TYPE_BETA_ENGINEER = 8
TIP_TYPE_BETA_ENGINEER_STR = "# ---------------Beta工程类提示 (原故障告警)------------"

NOTE_DICT = {
  TIP_TYPE_UNDEFINE: TIP_TYPE_UNDEFINE_STR,
  TIP_TYPE_STATE_TRANS: TIP_TYPE_STATE_TRANS_STR,
  TIP_TYPE_ACTIVE_FAILED: TIP_TYPE_ACTIVE_FAILED_STR,
  TIP_TYPE_INTELLIGENT_DRIVING: TIP_TYPE_INTELLIGENT_DRIVING_STR,
  TIP_TYPE_USER_INTERACTION: TIP_TYPE_USER_INTERACTION_STR,
  TIP_TYPE_ACTIVE_SAFETY: TIP_TYPE_ACTIVE_SAFETY_STR,
  TIP_TYPE_DRIVING_INTENT: TIP_TYPE_DRIVING_INTENT_STR,
  TIP_TYPE_IVI_FAULT: TIP_TYPE_IVI_FAULT_STR,
  TIP_TYPE_BETA_ENGINEER: TIP_TYPE_BETA_ENGINEER_STR,
}

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

def gen_msg_tip_id(csv_file, output_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_data = f.readlines()

    cur_tip_type = -1

    write_data = []

    for line in csv_data:
        try:
            tip_id = int(line.split(',')[0].strip())
        except:
            continue

        if tip_id == 0 or tip_id > 10000:
          tip_id_name = line.split(',')[1].strip()
          tip_id_note = line.split(',')[2].strip()

          tip_type = get_tip_type(int(tip_id))

          if tip_id >= 10100 and tip_id <= 10184:
            tip_id_note = "接管提醒_" + tip_id_note
          elif tip_id >= 10600 and tip_id <= 10684:
            tip_id_note = "激活失败_" + tip_id_note

          if tip_type != cur_tip_type:
            write_data.append("\n")
            write_data.append(NOTE_DICT[tip_type] + "\n")
            cur_tip_type = tip_type

          write_data.append(f"# {tip_id_note}\n")
          write_data.append(f"int32 {tip_id_name} = {tip_id}\n")

    with open(output_file, 'w', encoding='utf-8') as f:
      f.writelines(write_data)


def parse_args():
    parser = argparse.ArgumentParser(description='生成TipItem.msg中TIP_ID_XXX的定义')
    parser.add_argument('--csv', type=str, required=True, help='csv文件路径')
    parser.add_argument('--output', type=str, required=True, help='输出文件路径')
    return parser.parse_args()

def main():
    args = parse_args()
    csv_file = args.csv
    output_file = args.output

    gen_msg_tip_id(csv_file, output_file)


if __name__ == '__main__':
    main()