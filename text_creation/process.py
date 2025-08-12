import json 

# 获取conclusion
with open('../novel_chapter_info.json', 'r') as f:
    data = json.load(f)

conclusion = [i['conclusion'] for i in data]

with open('conclusion.md', 'w') as f:
    for i in conclusion:
        f.write(i + '\n')


# 获取last_ten_conclusion
with open('../novel_chapter_info_detailed.json', 'r') as f:
    data = json.load(f)

with open("last_ten_conclusion.md", "w") as f:
    for i in data[-10:]:
        title = i['title']
        conclusion = i['conclusion']
        f.write(f"## {title}\n\n{conclusion}\n\n")
    

with open("last_five_chapter.md", "w") as f:
    for i in data[-5:]:
        title = i['title']
        content = i['content']
        f.write(f"## {title}\n\n{content}\n\n")




