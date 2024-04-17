import matplotlib.pyplot as plt


def draw_line_chart(y_data, x_data, y_name, x_name):
    plt.figure(figsize=(30, 6))

    plt.plot(x_data, y_data)

    # plt.title('自定义样式折线图', fontsize=16)
    plt.xlabel(x_name, fontsize=10)
    plt.ylabel(y_name, fontsize=10)

    plt.grid(True)  # 添加网格线

    plt.show()
