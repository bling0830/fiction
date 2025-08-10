import os
def split_chapters(input_file, output_dir):
    # 读取文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按章节分割
    chapters = []
    current_chapter = []
    current_title = ""
    
    for line in content.split('\n'):
        if line.strip().startswith('第') and '章' in line:
            # 如果已经有内容,保存当前章节
            if current_chapter:
                chapters.append((current_title, '\n'.join(current_chapter)))
            # 开始新章节
            current_title = line.strip()
            current_chapter = [line]
        else:
            current_chapter.append(line)
    
    # 保存最后一章
    if current_chapter:
        chapters.append((current_title, '\n'.join(current_chapter)))
    
    # 写入单独的文件
    for title, content in chapters:
        # 提取章节号
        chapter_num = title.split('章')[0].strip('第')
        filename = f"{output_dir}/chapter_{chapter_num}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已保存: {filename}")

# 使用示例
files = os.listdir(".")
files = [f for f in files if f.endswith(".txt")]
for file in files:
    input_file = f"{file}"
    output_dir = f"chapters"
    os.makedirs(output_dir, exist_ok=True)
    # 调用函数
    split_chapters(input_file, output_dir)
    os.system(f"rm {output_dir}/chapter_.txt")