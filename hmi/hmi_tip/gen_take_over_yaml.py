import pandas as pd

# 加载 Excel 文件（请确保文件路径正确）
file_path = './test.xlsx'
sheet_data = pd.read_excel(file_path, sheet_name='Sheet1')

# 用于存储每个 YAML 块的字符串
yaml_blocks = []

state_list = ["智驾领航", "智能驾驶"]
take_over_list = ["转方向盘接管", "踩刹车接管", "acc_cancel_接管", "acc_on_off_接管"]

func_id = {
    "智驾领航": 10001,
    "智能驾驶": 10003
}

func_state_id = {
    "智驾领航": 20001,
    "智能驾驶": 20002
}

take_over_id = {
    "转方向盘接管": 1001,
    "踩刹车接管": 1004,
    "acc_cancel_接管": 1012,
    "acc_on_off_接管": 1010
}

# 遍历每一行，生成对应的 YAML 块
for index, row in sheet_data.iterrows():
    table_text = str(row[sheet_data.columns[0]]).strip()
    code = str(row[sheet_data.columns[1]])

    converted_code = "20" + code[-2:]

    for state in state_list:
        for take_over in take_over_list:
            scene_name = table_text + "-" + state + "-" + take_over

            block = (
                f'- scene_name: "{scene_name}"\n'
                f'  mock_sequence:\n'
                f'    - [{func_id[state]}, "OCCUR"]\n'
                f'    - 100\n'
                f'    - [{converted_code}, "OCCUR"]\n'
                f'    - 500\n'
                f'    - [{take_over_id[take_over]}, "OCCUR"]\n'
                f'  expect_tips:\n'
                f'    - meter:\n'
                f'        - [{func_id[state]}, "OCCUR"]\n'
                f'        - [{code}, "OCCUR"]\n'
                f'        - [{code}, "RESTORE"]\n'
                f'    - island:\n'
                f'        - [{func_state_id[state]}, "OCCUR"]\n'
                f'        - [{func_state_id[state]}, "RESTORE"]\n'
            )
            yaml_blocks.append(block)


# 拼接所有 YAML 块（块之间以空行分隔）
yaml_content = "\n".join(yaml_blocks)

# 保存到 YAML 文件
output_path = './test.yaml'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(yaml_content)

print("YAML 文件已生成，保存路径：", output_path)
