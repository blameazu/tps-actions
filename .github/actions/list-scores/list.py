import json
import os
from itertools import combinations

os.chdir(os.environ.get('GITHUB_WORKSPACE'))
GROUP_SIZE = int(os.environ.get('GROUPSIZE', 3))

with open('.problems.json', 'r', encoding='utf8') as f:
    problems = json.load(f)

scores = {}
allSubtasks = []
for pro in problems:
    scores[pro] = {}
    with open(os.path.join('p' + pro, 'subtasks.json'), 'r', encoding='utf8') as f:
        subtasks = json.load(f)
        for subid, subtask in subtasks['subtasks'].items():
            sid = '{}{}'.format(pro, subtask['index'])
            sc = subtask['score']
            scores[pro][subtask['index'] + 1] = sc
            if sc != 0:
            	allSubtasks.append({'id': sid, 'score': sc})

allSubtasks.sort(key=lambda v: v['score'])

total = sum([sub['score'] for sub in allSubtasks])
dp = [set() for _ in range(total + 1)]
dp[0].add(frozenset())

for sub in allSubtasks:
    sc = sub['score']
    sid = sub['id']
    for s in range(total - sc, -1, -1):
        snapshot = list(dp[s])
        for group in snapshot:
            if len(group) < GROUP_SIZE:
                new_group = set(group)
                new_group.add(sid)
                dp[s + sc].add(frozenset(new_group))

output = '| score | count | groups |\n'
output += '| --- | --- | --- |\n'
for s in range(1, total + 1):
    if len(dp[s]) > 1:
        output += '| {} | {} | {} |\n'.format(
            s,
            len(dp[s]),
            ' '.join(
                '(' + ', '.join(sorted(g)) + ')' for g in dp[s]
            )
        )

reportpath = os.environ.get('REPORTPATH')
try:
    with open(reportpath, 'r', encoding='utf8') as f:
        text = f.read()
except FileNotFoundError:
    text = ''

flag1 = '<!-- scores start -->'
flag2 = '<!-- scores end -->'
if flag1 not in text or flag2 not in text:
    text += '\n## Scores\n{}\n{}\n'.format(flag1, flag2)
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)
else:
    idx1 = text.index(flag1)
    idx2 = text.index(flag2)

text = text[:idx1] + flag1 + '\n\n' + output + '\n' + text[idx2:]
with open(reportpath, 'w', encoding='utf8') as f:
    f.write(text)
