import pymupdf
import textwrap
from openai import OpenAI

# OpenAI API密钥
API_KEY = ""

# 使用API密钥创建OpenAI客户端
client = OpenAI(api_key=API_KEY)


def extract_text_from_pdf(pdf_path):
    # 打开文档
    doc = pymupdf.open(pdf_path)

    text = ""  # 我们将返回此字符串
    row_count = 0  # 计数表格行数
    header = ""  # 整体表头：只输出一次！

    # 遍历页面
    for page in doc:
        # 仅读取每页上的表格行，忽略其他内容
        tables = page.find_tables()  # 一个"TableFinder"对象
        for table in tables:

            # 在第一页提取外部列名（如果有）
            if page.number == 0 and table.header.external:
                # 构建整体表头字符串
                # 技术说明：不完整/复杂的表格可能在一些表头单元格中有"None"。此时仅使用空字符串。
                header = (
                    ";".join(
                        [
                            name if name is not None else ""
                            for name in table.header.names
                        ]
                    )
                    + "\n"
                )
                text += header
                row_count += 1  # 增加行数计数

            # 输出表格主体
            for row in table.extract():  # 遍历表格行

                # 再次将单元格中的任何"None"替换为空字符串
                row_text = (
                    ";".join([cell if cell is not None else "" for cell in row]) + "\n"
                )
                if row_text != header:  # 省略表头行的重复
                    text += row_text
                    row_count += 1  # 增加行数计数
    doc.close()  # 关闭文档
    print(f"从文件 '{doc.name}' 加载了 {row_count} 行表格数据。\n")
    return text


# 使用模型 "gpt-3.5-turbo-instruct" 生成文本
def generate_response_with_chatgpt(prompt):
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",  # 选择合适的模型
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()


filename = "C:\\Users\\CalLee\\Desktop\\solana-gent\\solana-whitepaper-en.pdf"
pdf_text = extract_text_from_pdf(filename)

print("准备就绪 - 提问或输入q/Q退出：")
while True:
    user_query = input("==> ")
    if user_query.lower().strip() == "q":
        break
    prompt = pdf_text + "\n\n" + user_query
    response = generate_response_with_chatgpt(prompt)
    print("回复:\n")
    for line in textwrap.wrap(response, width=70):
        print(line)
    print("-" * 10)
