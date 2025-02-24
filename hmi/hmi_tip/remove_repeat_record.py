import pandas as pd

def remove_duplicates_from_csv(file_path):
    """
    从CSV文件中删除重复记录并保存

    Args:
        file_path: CSV文件路径
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)

        # 删除重复行
        df_no_duplicates = df.drop_duplicates()

        # 保存到原文件
        df_no_duplicates.to_csv(file_path, index=False)
        print(f"成功处理文件: {file_path}")
        print(f"删除了 {len(df) - len(df_no_duplicates)} 条重复记录")

    except Exception as e:
        print(f"处理文件时出错: {str(e)}")

if __name__ == "__main__":
    # 使用示例
    file_path = "test.csv"  # 替换为实际的CSV文件路径
    remove_duplicates_from_csv(file_path)
