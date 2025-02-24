import yaml
import csv
import os

def extract_scene_names():
    # 定义输入和输出文件路径
    yaml_path = "test.yaml"  # yaml文件所在目录
    output_csv = "scene_names.csv"  # 输出的CSV文件名

    scene_names = []

    # 读取yaml文件
    with open(yaml_path, "r") as f:
        yaml_data = yaml.safe_load(f)
        for mocker_scence in yaml_data:
            scene_name = mocker_scence["scene_name"]
            scene_names.append(scene_name)

    # 将场景名称写入CSV文件
    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Scene Name'])  # 写入表头
        for scene_name in scene_names:
            writer.writerow([scene_name])

    print(f"Successfully extracted {len(scene_names)} scene names to {output_csv}")

if __name__ == "__main__":
    extract_scene_names()
