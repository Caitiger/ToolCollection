import fitz
import os
import re

WORK_PATH = './'


def save_pdf(pdf_name, start_page_num, last_page_num, pdf):
    print(pdf_name)
    print(str(start_page_num))
    print(str(last_page_num))

    pdf_writer = fitz.open()
    pdf_writer.insert_pdf(pdf, from_page=start_page_num, to_page=last_page_num)

    pdf_writer.save(pdf_name)
    pdf_writer.close


def get_new_pdf_info(pdf, pdf_path, pdf_file, start_page_num, last_page_num, pdf_name, page, form_class):
    page_contents = page.get_text().strip().split('\n')

    for content in page_contents:
        if "总金额（小写）" in content:
            money = content.split()[-1]
            money = ''.join(re.findall(r'[0-9.]+', money))
            break

    name = page_contents[0].split()[0].split('-')[-1]
    form_num = page_contents[1].split(':')[-1].strip()

    pdf_dir = pdf_path + '/' + pdf_file.split('.')[0] + '-' + form_class
    if not os.path.exists(pdf_dir):
        os.mkdir(pdf_dir)

    if start_page_num != last_page_num:
        save_pdf(pdf_name, start_page_num, last_page_num, pdf)

    pdf_name = pdf_dir + '/' + name + '-' + form_num + '-' + money + '.pdf'

    return pdf_name


def split_pdf(pdf_path, pdf_file):
    print("=============================================" + pdf_file + "=============================================")

    pdf = fitz.open(pdf_path + pdf_file)
    num_pages = pdf.page_count

    pdf_path = os.path.dirname(os.path.realpath(pdf_path + pdf_file))

    pdf_name = ''

    for page_num in range(num_pages):
        page = pdf[page_num]
        if 0 == page_num:
            start_page_num = page_num
            last_page_num = page_num

        if ("差旅报销单" in page.get_text()) or ("日常报销单" in page.get_text() and "代垫费用" in page.get_text()):
            pdf_name = get_new_pdf_info(pdf, pdf_path, pdf_file, start_page_num, last_page_num, pdf_name, page, "差旅报销单")
            start_page_num = page_num
        elif "日常报销单" in page.get_text():
            pdf_name = get_new_pdf_info(pdf, pdf_path, pdf_file, start_page_num, last_page_num, pdf_name, page, "日常报销单")
            start_page_num = page_num

        last_page_num = page_num

        if page_num == num_pages - 1:
            save_pdf(pdf_name, start_page_num, last_page_num, pdf)


def main(pdf_path):
    print(pdf_path)
    for file in os.listdir(pdf_path):
        if os.path.isfile(pdf_path + file) and file.split('.')[-1] == "pdf":
            split_pdf(pdf_path, file)


if __name__ == "__main__":
    main(WORK_PATH)
