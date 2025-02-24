import argparse
from collections import defaultdict

TO_S = 10100
TO_E = 10184

AF_S = 10600
AF_E = 10684

PNC_PREFIX = "foxglove_msgs::msg::Pnc2HmiState::PNC_IHBTRESN_"
TIP_ITEM_PREFIX = "hmi_msgs::msg::TipItem::"

def get_key_value(line):
    suffix_list = line.split(',')[1].strip().split('_')[3:]
    suffix = "_".join(suffix_list)
    key = PNC_PREFIX + suffix
    value = TIP_ITEM_PREFIX + str(line.split(',')[1].strip())
    return key, value

def switch_ihbtresn_id(csv_file, output_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pnc_hmi_id_dict = defaultdict(dict)

    for line in lines:
        if 'TIP_ID_' in line:
            tip_id = int(line.split(',')[0].strip())
            if tip_id >= TO_S and tip_id <= TO_E:
                key, value = get_key_value(line)
                pnc_hmi_id_dict[key]["takeover"] = value
            elif tip_id >= AF_S and tip_id <= AF_E:
                key, value = get_key_value(line)
                pnc_hmi_id_dict[key]["inherit"] = value


    switch_code = []
    for key, value in pnc_hmi_id_dict.items():
        if len(value) == 2:
            switch_code.append(f"    case {key}:")
            switch_code.append("      if (ReasonType::REASON_TYPE_TAKEOVER == reason_type) {")
            switch_code.append(f"        return {value['takeover']};")
            switch_code.append("      } else if (ReasonType::REASON_TYPE_INHERBIT == reason_type) {")
            switch_code.append(f"        return {value['inherit']};")
            switch_code.append("      } else {")
            switch_code.append("        break;")
            switch_code.append("      }")
        elif len(value) == 1:
            if "takeover" in value.keys():
                switch_code.append(f"    case {key}:")
                switch_code.append("      if (ReasonType::REASON_TYPE_TAKEOVER == reason_type) {")
                switch_code.append(f"        return {value['takeover']};")
                switch_code.append("      } else {")
                switch_code.append("        break;")
                switch_code.append("      }")
            elif "inherit" in value.keys():
                switch_code.append(f"    case {key}:")
                switch_code.append("      if (ReasonType::REASON_TYPE_INHERBIT == reason_type) {")
                switch_code.append(f"        return {value['inherit']};")
                switch_code.append("      } else {")
                switch_code.append("        break;")
                switch_code.append("      }")


    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(switch_code))



def parse_args():
    parser = argparse.ArgumentParser(description='转换ihbtresn_id')
    parser.add_argument('--csv', type=str, required=True, help='csv文件路径')
    parser.add_argument('--output', type=str, required=True, help='输出文件路径')
    return parser.parse_args()

def main():
    args = parse_args()
    csv_file = args.csv
    output_file = args.output

    switch_ihbtresn_id(csv_file, output_file)

if __name__ == '__main__':
    main()
