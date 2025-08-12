from openai import OpenAI
import re
import json
from tqdm import tqdm
import os
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor
from novel_prompt import SPLIT_SYSTEM

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
        max_tokens=32768
    )
    
    # print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def split_fiction(merge, content):
    content = f"""
## 【设定总结】
{merge}

## 【已有文章】
{content}
"""

    messages = [
        {"role": "system", "content": SPLIT_SYSTEM},
        {"role": "user", "content": content},
    ]
    result = call_kimi(messages)
    return result


if __name__ == "__main__":
    with open("merge.md", "r") as f:
        merge = f.read()
    with open("continue_writing.md", "r") as f:
        content = f.read()
    result = split_fiction(merge, content)
    with open("split.md", "w") as f:
        f.write(result)