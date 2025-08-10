from openai import OpenAI
from novel_prompt import CHAPTER_CONCLUSION_SYSTEM, NOVEL_SETTING_SYSTEM, DETAILED_CHAPTER_CONCLUSION_SYSTEM
import re
import json
from tqdm import tqdm
import os
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor

def call_kimi(messages):
    from openai import OpenAI

    client = OpenAI(
        api_key="sk-8XckQddnn9LBMsAEHcXOx3wImckQ4EhpTAN8Z9AnQ5iWWZKc", # 在这里将 MOONSHOT_API_KEY 替换为你从 Kimi 开放平台申请的 API Key
        base_url="https://api.moonshot.cn/v1",
    )
    
    completion = client.chat.completions.create(
        model = "kimi-k2-0711-preview",
        messages = messages,
        temperature = 0.6,
    )
    
    # print(completion.choices[0].message.content)
    return completion.choices[0].message.content

# 章节拆分
def chapter_split(text):

    pattern = re.compile(r'(第\d+章\s*.*)')

    parts = pattern.split(text)

    chapters = []
    # 列表的第一个元素是引言（如果存在）
    intro = parts[0].strip()

    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        # 确保内容部分存在
        if i + 1 < len(parts):
            content = parts[i+1].strip()
        else:
            content = "" # 如果这是最后一章，可能没有后续内容
        
        chapters.append({'title': title, 'content': content})

    return chapters

# 总结全文
def novel_conclusion(chapter_list):
    for ch in tqdm(chapter_list, desc="正在处理章节"):
        call_messages = [
            {"role": "system", "content": DETAILED_CHAPTER_CONCLUSION_SYSTEM},
            {"role": "user", "content": ch["content"]}
        ]
        res = call_kimi(call_messages)
        ch["conclusion"] = res
    return chapter_list

# def main_chapter_conclusion(file_list, output_path):
#     final_res = []
#     for file in tqdm(file_list, desc="正在处理文件"):
#         with open(file,'r', encoding='utf-8') as f:
#             text = f.read()
#             chapter_list = chapter_split(text)
#             res_list = novel_conclusion(chapter_list)
#             final_res.extend(res_list)
#     with open(output_path, "w") as f_out:
#         f_out.write(json.dumps(final_res, ensure_ascii=False, indent=4))

def process_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        chapter_list = chapter_split(text)
        res_list = novel_conclusion(chapter_list)
    return file, res_list

def main_chapter_conclusion(file_list, output_path):
    processed_files = set()
    final_res = []
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f_out:
            try:
                final_res = json.load(f_out)
                processed_files = set(item["file"] for item in final_res if "file" in item)
            except Exception:
                pass

    files_to_process = [f for f in file_list if f not in processed_files]

    # 用 ThreadPoolExecutor 替换 ProcessPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_file, file): file for file in files_to_process}

        for future in tqdm(as_completed(futures), total=len(files_to_process), desc="处理文件"):
            try:
                file, res_list = future.result()
                for item in res_list:
                    item['file'] = file
                final_res.extend(res_list)
                def _file_index(name):
                    m = re.search(r'(\d+)', name or "")
                    return int(m.group(1)) if m else float('inf')

                final_res_sorted = sorted(final_res, key=lambda x: _file_index(x.get("file", "")))
                with open(output_path, 'w', encoding='utf-8') as f_out:
                    json.dump(final_res_sorted, f_out, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"处理文件 {futures[future]} 时发生错误: {str(e)}")
            
# 总结设定
def setting_conclusion(chapter_list, prev_setting):
    for ch in tqdm(chapter_list, desc="正在处理章节"):
        input_str = f"【旧设定文档】\n{prev_setting}\n【最新章节内容】\n{ch["content"]}"

        call_messages = [
            {"role": "system", "content": NOVEL_SETTING_SYSTEM},
            {"role": "user", "content": ch["content"]}
        ]
        res = call_kimi(call_messages)
        with open("temp.txt", "w") as f_out:
            f_out.write(res)
        ch["setting"] = res
        prev_setting = res
    return prev_setting

def main_setting_conclusion(file_list, output_path):
    final_res = []
    setting_res = ""
    for file in tqdm(file_list, desc="正在处理文件"):
        with open(file,'r', encoding='utf-8') as f:
            text = f.read()
            chapter_list = chapter_split(text)
            setting_res = setting_conclusion(chapter_list, setting_res)
            final_res.extend(chapter_list)
    with open(output_path, "w") as f_out:
        f_out.write(json.dumps(final_res, ensure_ascii=False, indent=4))



if __name__ == "__main__":
    # call_kimi([{"role": "user", "content": "test"}])
    file_list = os.listdir("chapters")
    file_list = [f"chapters/{f}" for f in file_list]
    # file_list = file_list[:10]
    output_path = "novel_chapter_info_detailed.json"
    main_chapter_conclusion(file_list, output_path)