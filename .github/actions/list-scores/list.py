import json
import os

os.chdir(os.environ.get('GITHUB_WORKSPACE'))
GROUP_SIZE = int(os.environ.get('GROUPSIZE', 3))

# 读取所有题目及其子任务分数
with open('.problems.json', 'r', encoding='utf8') as f:
    problems = json.load(f)

# 将每个子任务记录成一个列表，格式为 {'id': '题目编号+子任务序号', 'score': 分数}
all_subtasks = []
for pro in problems:
    with open(os.path.join('p' + pro, 'subtasks.json'), 'r', encoding='utf8') as f:
        subtasks = json.load(f)
        for subid, subtask in subtasks['subtasks'].items():
            sc = subtask['score']
            if sc != 0:
                sid = '{}{}'.format(pro, subtask['index'])
                all_subtasks.append({'id': sid, 'score': sc})

# 按分数升序排列（可选，仅为了逻辑清晰）
all_subtasks.sort(key=lambda v: v['score'])

# 计算所有子任务分数之和
total_score = sum(sub['score'] for sub in all_subtasks)

# dp_count[j][s] 表示：用恰好 j 个子任务凑出总分 s 的方案数
# 这里 j 从 0 到 GROUP_SIZE，s 从 0 到 total_score
# 为了节省内存，可以把 list-of-list 初始化为 0
dp_count = [ [0] * (total_score + 1) for _ in range(GROUP_SIZE + 1) ]
# 边界：用 0 个子任务凑出总分 0 有 1 种方法（选都不选）
dp_count[0][0] = 1

# 遍历每个子任务，做“01背包”转移
for sub in all_subtasks:
    sc = sub['score']
    # 必须倒序枚举 j 与 s，保证每个子任务只被选一次
    for j in range(GROUP_SIZE, 0, -1):
        for s in range(total_score, sc - 1, -1):
            dp_count[j][s] += dp_count[j - 1][s - sc]

# 生成输出字符串，不再列出具体组合，只显示：分数 s、组合方案数 count
output = '| score | count |\n'
output += '| --- | --- |\n'
for s in range(1, total_score + 1):
    # 统计使用 1 到 GROUP_SIZE 个子任务凑出分数 s 的总方案数
    count = sum(dp_count[j][s] for j in range(1, GROUP_SIZE + 1))
    if count > 1:
        output += f'| {s} | {count} |\n'

# 将结果插入到 REPORTPATH 指定的报告文件中
reportpath = os.environ.get('REPORTPATH')
try:
    with open(reportpath, 'r', encoding='utf8') as f:
        text = f.read()
except FileNotFoundError:
    text = ''

flag1 = '<!-- scores start -->'
flag2 = '<!-- scores end -->'
if flag1 not in text or flag2 not in text:
    # 如果没有标记，就插入新的区块
    text += f'\n## Scores\n{flag1}\n{flag2}\n'
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)
else:
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)

# 用新的 output 覆盖原来标记区间
text = text[:idx1] + flag1 + '\n\n' + output + '\n' + text[idx2:]
with open(reportpath, 'w', encoding='utf8') as f:
    f.write(text)
