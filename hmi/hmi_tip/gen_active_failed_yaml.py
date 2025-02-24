import pandas as pd

# 加载 Excel 文件（请确保文件路径正确）
file_path = './test.xlsx'
sheet_data = pd.read_excel(file_path, sheet_name='Sheet1')

# 用于存储每个 YAML 块的字符串
yaml_blocks = []

# 遍历每一行，生成对应的 YAML 块
for index, row in sheet_data.iterrows():
    table_text = str(row[sheet_data.columns[0]]).strip()
    code = str(row[sheet_data.columns[1]])
    # 根据示例，转换后的代码 = 表格代码 - 8100
    converted_code = "20" + code[-2:]

    table_text = table_text.replace("【新】", "激活失败-")

    scene_name = table_text + "-acc enable-智驾领航"

    # 严格按照示例格式构造 YAML 块
    block = (
        f'- scene_name: "{scene_name}"\n'
        f'  mock_sequence:\n'
        f'    - [{converted_code}, "OCCUR"]\n'
        f'    - [1006, "OCCUR"]\n'
        f'    - [1011, "OCCUR"]\n'
        f'  expect_tips:\n'
        f'    - meter:\n'
        f'        - [{code}, "OCCUR", "", "0"]\n'
    )
    yaml_blocks.append(block)

for index, row in sheet_data.iterrows():
    table_text = str(row[sheet_data.columns[0]]).strip()
    code = str(row[sheet_data.columns[1]])
    # 根据示例，转换后的代码 = 表格代码 - 8100
    converted_code = "20" + code[-2:]

    table_text = table_text.replace("【新】", "激活失败-")

    scene_name = table_text + "-acc on/off-智驾领航"

    # 严格按照示例格式构造 YAML 块
    block = (
        f'- scene_name: "{scene_name}"\n'
        f'  mock_sequence:\n'
        f'    - [{converted_code}, "OCCUR"]\n'
        f'    - [1006, "OCCUR"]\n'
        f'    - [1010, "OCCUR"]\n'
        f'  expect_tips:\n'
        f'    - meter:\n'
        f'        - [{code}, "OCCUR", "", "0"]\n'
    )
    yaml_blocks.append(block)


# 遍历每一行，生成对应的 YAML 块
for index, row in sheet_data.iterrows():
    table_text = str(row[sheet_data.columns[0]]).strip()
    code = str(row[sheet_data.columns[1]])
    # 根据示例，转换后的代码 = 表格代码 - 8100
    converted_code = "20" + code[-2:]

    table_text = table_text.replace("【新】", "激活失败-")

    scene_name = table_text + "-acc enable-智能驾驶"

    # 严格按照示例格式构造 YAML 块
    block = (
        f'- scene_name: "{scene_name}"\n'
        f'  mock_sequence:\n'
        f'    - [{converted_code}, "OCCUR"]\n'
        f'    - [1011, "OCCUR"]\n'

        f'  expect_tips:\n'
        f'    - meter:\n'
        f'        - [{code}, "OCCUR", "", "1"]\n'
    )
    yaml_blocks.append(block)

for index, row in sheet_data.iterrows():
    table_text = str(row[sheet_data.columns[0]]).strip()
    code = str(row[sheet_data.columns[1]])
    # 根据示例，转换后的代码 = 表格代码 - 8100
    converted_code = "20" + code[-2:]

    table_text = table_text.replace("【新】", "激活失败-")

    scene_name = table_text + "-acc on/off-智能驾驶"

    # 严格按照示例格式构造 YAML 块
    block = (
        f'- scene_name: "{scene_name}"\n'
        f'  mock_sequence:\n'
        f'    - [{converted_code}, "OCCUR"]\n'
        f'    - [1010, "OCCUR"]\n'
        f'  expect_tips:\n'
        f'    - meter:\n'
        f'        - [{code}, "OCCUR", "", "1"]\n'
    )
    yaml_blocks.append(block)

# 拼接所有 YAML 块（块之间以空行分隔）
yaml_content = "\n".join(yaml_blocks)

# 保存到 YAML 文件
output_path = './test.yaml'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(yaml_content)

print("YAML 文件已生成，保存路径：", output_path)
