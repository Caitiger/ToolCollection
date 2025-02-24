import argparse

def add_note(msg_file, proto_file, output_file):
    # 读取文件A的内容
    with open(msg_file, 'r', encoding='utf-8') as f:
        lines_msg = f.readlines()

    # 读取文件B的内容
    with open(proto_file, 'r', encoding='utf-8') as f:
        lines_proto = f.readlines()

    # 存储修改后的B文件内容
    new_lines_proto = lines_proto.copy()

    # 遍历文件B的每一行
    for i, line_proto in enumerate(lines_proto):
        # 遍历文件A的每一行（从第二行开始）
        if "=" in line_proto:
          print(line_proto)
          for j in range(1, len(lines_msg)):
            if len(lines_msg[j].strip().split(' ')) >= 2:
              # 如果B中当前行与A中某行相同
              proto_item = str(line_proto.split('=')[0].strip().split(' ')[-1])
              msg_item = str(lines_msg[j].strip().split(' ')[1])

              print(f"proto_item: {proto_item}, msg_item: {msg_item}")

              if proto_item == msg_item:
                  # 在B文件该行末尾添加A文件中的前一行内容
                  new_lines_proto[i] = str(line_proto.rstrip()) + '  // ' + lines_msg[j-1].strip().split('#')[-1] + '\n'
                  break

    # 将修改后的内容写回文件B
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines_proto)

def parse_args():
    parser = argparse.ArgumentParser(description='为proto添加注释')
    parser.add_argument('--msg', type=str, required=True, help='msg文件路径')
    parser.add_argument('--proto', type=str, required=True, help='proto文件路径')
    parser.add_argument('--output', type=str, required=True, help='输出文件路径')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    msg_file = args.msg
    proto_file = args.proto
    output_file = args.output

    add_note(msg_file, proto_file, output_file)
