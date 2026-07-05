#!/usr/bin/env python3
"""
斩除题目：从 questions.json 删除指定题号，重建 quiz.html，提交推送到 GitHub。

用法：python delete_questions.py <题号1> [题号2] ...
示例：python delete_questions.py 5 15 23
"""
import json, sys, os, subprocess

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 2:
    print('用法: python delete_questions.py <题号1> [题号2] ...')
    sys.exit(1)

to_delete = set(int(x) for x in sys.argv[1:])
print(f'待删题号: {sorted(to_delete)}')

path = os.path.join(BASE, 'questions.json')
with open(path, encoding='utf-8') as f:
    qs = json.load(f)

before = len(qs)
removed = [q for q in qs if q['num'] in to_delete]
qs = [q for q in qs if q['num'] not in to_delete]

# 重新编号
for i, q in enumerate(qs, 1):
    q['num'] = i

with open(path, 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

print(f'已删除 {before - len(qs)} 题，剩余 {len(qs)} 题')
for q in removed:
    print(f'  - Q{q["num"]} [{q["author"]}]: {q["question"][:40]}')

# 重建 quiz.html
print('\n重建 quiz.html...')
subprocess.run([sys.executable, os.path.join(BASE, 'build_quiz.py')], cwd=BASE)

# Git commit & push
deleted_list = ' '.join(str(n) for n in sorted(to_delete))
msg = f'斩除题目 Q{deleted_list}，剩余 {len(qs)} 题'
print(f'\nGit: {msg}')
subprocess.run(['git', 'add', 'questions.json', 'quiz.html'], cwd=BASE)
subprocess.run(['git', 'commit', '-m', msg], cwd=BASE)
subprocess.run(['git', 'push', 'origin', 'main'], cwd=BASE)
print('\n完成！')
