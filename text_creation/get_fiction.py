from openai import OpenAI
import re
import json
from tqdm import tqdm
import os
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor
from novel_prompt import MERGE_SETTING_SYSTEM, CONTINUE_WRITING_SYSTEM, CONTINUE_WRITING_SYSTEM_V3

def call_kimi(messages):
    from openai import OpenAI

    # client = OpenAI(
    #     api_key="sk-8XckQddnn9LBMsAEHcXOx3wImckQ4EhpTAN8Z9AnQ5iWWZKc", # 在这里将 MOONSHOT_API_KEY 替换为你从 Kimi 开放平台申请的 API Key
    #     base_url="https://api.moonshot.cn/v1",
    # )
    client = OpenAI(api_key="sk-a074425aea0641c9bf277864ac399f73", base_url="https://api.deepseek.com")
    
    completion = client.chat.completions.create(
        # model = "kimi-k2-0711-preview",
        model = "deepseek-reasoner",
        messages = messages,
        temperature = 0.6,
        max_tokens=32768
    )
    
    # print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def merge_setting():
    with open("last_ten_conclusion.md", "r", encoding='utf-8') as f:
        last_ten_conclusion = f.read()
    
    messages = [
        {"role": "system", "content": MERGE_SETTING_SYSTEM},
        {"role": "user", "content": last_ten_conclusion},
    ]
    if os.path.exists("merge.md"):
        return
    result = call_kimi(messages)
    with open("merge.md", "w") as f:
        f.write(result)


def continue_writing(conclusion, merge, last_five_fictions):
    user_content = f"""小说大纲：
{conclusion}

前10章设定总结：
{merge}

前5章正文：
{last_five_fictions}
"""

    messages = [
        {"role": "system", "content": CONTINUE_WRITING_SYSTEM},
        {"role": "user", "content": user_content},
    ]

    result = call_kimi(messages)
    with open("continue_writing.md", "w") as f:
        f.write(result)

def continue_writing_with_title_and_outline(conclusion, merge, last_five_fictions, title, outline):
    user_content = f"""
## 前文大纲
{conclusion}

## 前10章设定总结
{merge}

## 前5章正文
{last_five_fictions}

## 新一章的章节标题
{title}

## 新一章的大纲
{outline}
"""

    messages = [
        {"role": "system", "content": CONTINUE_WRITING_SYSTEM_V3},
        {"role": "user", "content": user_content},
    ]

    result = call_kimi(messages)
    with open("continue_writing_with_title_and_outline.md", "w", encoding='utf-8') as f:
        f.write(result)

if __name__ == "__main__":
    merge_setting()
    with open("conclusion.md", "r", encoding='utf-8') as f:
        conclusion = f.read()
    with open("merge.md", "r", encoding='utf-8') as f:
        merge = f.read()
    with open("last_five_chapter.md", "r", encoding='utf-8') as f:
        last_five_fictions = f.read()
    # continue_writing(conclusion, merge, last_five_fictions)

    title = "乳白晶体的低语"
    outline = "返回途中，泰坦解析晶体坐标，指向月球背面“雨海-A”陨坑；林栋决定48小时内启动绝密登月计划，需同时说服NASA与SpaceX高层。"
    continue_writing_with_title_and_outline(conclusion, merge, last_five_fictions, title, outline)