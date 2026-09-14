"""按来源章节确定性拆分；依赖 lxml，将章节直接生成 Markdown。重复运行会覆盖生成文件。"""
from pathlib import Path
import re
import html
import hashlib
import json
import os
from html转markdown import convert_html

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / '原始资料'
ORIG.mkdir(exist_ok=True)
names = ['26年同济CS预推免复习资料_离线完整版.html', '27届预推免笔试.txt', '27届预推免面试.txt', '27届预推免机试.txt.txt', '机试.jpg']
for name in names:
    src, dst = ROOT / name, ORIG / name
    if src.exists() and not dst.exists():
        assert src.resolve().parent == ROOT and dst.resolve().parent == ORIG
        src.rename(dst)
source = ORIG / names[0]
raw = source.read_text(encoding='utf-8')
sections = {int(n): b for n, b in re.findall(r'<section class="doc" id="s(\d+)">(.*?)</section>', raw, re.S)}
css = re.search(r'<style>(.*?)</style>', raw, re.S)[1]
records = []

def text(s):
    return html.unescape(re.sub('<[^>]*>', '', s)).strip()

def archive_path(path):
    parts = Path(path).parts
    if parts[0].isdigit() and len(parts) == 3:
        event = parts[2].split('-')[0]
        assert event in ['预推免', '夏令营', '考研复试']
        return '/'.join([event, *parts])
    return path

def write(path, content):
    path = archive_path(path)
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')

def save(path, n, fragment=None, note='回忆及整理资料，非官方试卷；原有题解和补编内容未经逐题校验。'):
    path = archive_path(path)
    body = sections[n] if fragment is None else fragment
    body = re.sub(r'<a[^>]*class="backtop"[^>]*>.*?</a>', '', body, flags=re.S)
    title = Path(path).stem
    origin = re.search(r'<p class="src">(.*?)</p>', sections[n], re.S)[1]
    rel = Path(os.path.relpath(source, (ROOT / path).parent)).as_posix()
    body = re.sub(r'href="#(s\d+)"', lambda m: 'href="' + rel + '#' + m[1] + '"', body)
    page = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + html.escape(title) + '</title><style>' + css + '\n#main{margin:0 auto;max-width:1000px;padding:24px}.archive-note{background:#fff7ed;padding:14px;border:1px solid #fed7aa}</style></head><body><main id="main"><p><a href="' + rel + '#s' + str(n) + '">查看原始资料对应章节</a></p><div class="archive-note">' + html.escape(note) + '</div><p>' + origin + '</p><article class="doc">' + body + '</article></main></body></html>'
    path = str(Path(path).with_suffix(".md")).replace("\\", "/")
    write(path, convert_html(page))
    records.append({'path': path, 'section': 's' + str(n), 'source': source.relative_to(ROOT).as_posix(), 'note': note})

def chunks(n, level, pattern):
    b = sections[n]
    hs = [m for m in re.finditer(r'<h'+str(level)+r'[^>]*>(.*?)</h'+str(level)+r'>', b, re.S) if re.search(pattern, text(m[1]))]
    return [(text(m[1]), b[m.start():hs[i+1].start() if i+1<len(hs) else len(b)]) for i,m in enumerate(hs)]

def split_questions(n, level, pattern, folder, prefix, note):
    for i,(title,body) in enumerate(chunks(n,level,pattern),1):
        title = re.sub(r'[<>:"/\\|?*]', '-', title)
        save(f'{folder}/{prefix}-{i:02d}-{title}.html',n,body,note)

# 2023 年：原章节明确区分了夏令营与预推免。
b=sections[27]
for typ,start,end in [('机试',274,7520),('笔试',7520,7737),('面试',7737,8625)]:
    save(f'2023/{typ}/夏令营-回忆.html',27,b[start:end])
for typ,start,end in [('机试',8625,37930),('笔试',37930,38427),('面试',38427,len(b))]:
    save(f'2023/{typ}/预推免-回忆.html',27,b[start:end], '回忆及补编资料，非官方试卷。机试第一题引用同年夏令营第一题；原资料的列位置输出描述与示例存在歧义，请结合原文核实。')

# 2024 年：软院预推免与夏令营分开；切片为已核对的段落边界。
b=sections[26]
for typ,body in [('笔试',b[218:765]+b[859:1008]),('机试',b[765:859]),('面试',b[1008:1196])]:
    save(f'2024/{typ}/夏令营-回忆.html',26,body)
for typ,start,end in [('机试',1288,1509),('面试',1509,1626),('笔试',1626,1737)]:
    save(f'2024/{typ}/预推免-软件学院回忆.html',26,b[1196:1288]+b[start:end], '来源明确为软件学院预推免经验，勿当作所有计算机方向统一试卷。原文“无向图求关键路径”等表述存疑，保留待核。')
split_questions(25,2,r'第.题|综合模拟题|总结与建议','2024/笔试','预推免-补编', '本篇含“根据回忆补全的题目”、知识点讲解及模拟练习，不能视为完整原题。原解析可能有误，例如127结点满二叉树第7层64结点应为填满。')

# 2025 年。
b=sections[23]
save('2025/笔试/预推免-回忆.html',23,b[200:1995])
save('2025/面试/预推免-回忆.html',23,b[1995:])
split_questions(24,2,r'^P\d','2025/机试','预推免','来源称真题，实际为民间回忆与整理，含参考题解；未验证题解正确性。')
for typ,n in [('笔试',20),('机试',21),('面试',22)]:
    save(f'2025/{typ}/夏令营-回忆与复习资料.html',n)

# 其他历史考试单列在文件名前缀中，保持“年份 / 考核类型”结构。
save('2020/机试/夏令营-题目与解析.html',30)
for title,body in chunks(29,2,r'202[234]年|附录'):
    if title.startswith('202'):
        save(f'{title[:4]}/机试/考研复试-题目与解析.html',29,body)
    else:
        save('通用复习/机试/考研复试-备考建议.html',29,body)
for year,typ,n in [(2025,'笔试',28),(2025,'机试',32),(2025,'面试',33),(2024,'笔试',38),(2023,'笔试',39)]:
    save(f'{year}/{typ}/考研复试-回忆与解析.html',n)
for typ,n in [('笔试',0),('面试',31),('面试',35),('面试',37)]:
    title=text(re.search(r'<h1[^>]*>(.*?)</h1>',sections[n],re.S)[1])
    save(f'通用复习/{typ}/{title}.html',n)

# 27届原始回忆：使用围栏保留机试样例空格，原文不改写。
for typ in ['笔试','面试']:
    name=f'27届预推免{typ}.txt'
    write(f'2026/{typ}/预推免-27届回忆.md',f'# 27届预推免{typ}回忆\n\n年份暂按2026年考试（2027届）归档，原文未注明日期，待核实。\n\n来源：[原始文本](../../../原始资料/{name})。\n\n'+(ORIG/name).read_text(encoding='utf-8'))
b=(ORIG/'27届预推免机试.txt.txt').read_text(encoding='utf-8')
matches=list(re.finditer(r'^([1-4])，',b,re.M))
titles=['数字定位与格式化输出','十进制数位和整除统计','二分访问层次格式化输出','循环序列更新查询']
for i,m in enumerate(matches):
    frag=b[m.start():matches[i+1].start() if i+1<len(matches) else len(b)]
    note='第2题样例输入与n=7不一致，解释额外计入了末尾基数3；按正文的7个数统计应为3个，原回忆写4，待核实。' if i==1 else ('操作是同步更新还是依次原地更新未明确；取模边界写为大于而非大于等于，均保留待核实。' if i==3 else '格式化空格及细节以原始资料为准。')
    write(f'2026/机试/预推免-{i+1:02d}-{titles[i]}.md',f'# {titles[i]}\n\n年份暂按2026年考试（2027届）归档，待核实。\n\n来源：[27届机试原文](../../../原始资料/27届预推免机试.txt.txt)。\n\n{b[:matches[0].start()].strip()}\n\n整理备注：{note}\n\n## 原文\n\n```text\n{frag.rstrip()}\n```\n')
write('原始资料/SHA256.json',json.dumps({n:hashlib.sha256((ORIG/n).read_bytes()).hexdigest() for n in names},ensure_ascii=False,indent=2)+'\n')
write('来源索引.json',json.dumps(records,ensure_ascii=False,indent=2)+'\n')

# 可点击总目录，未抽取的通用知识点仍可由完整版目录访问。
intro='''# 同济大学计算机推免与复试题目档案

按**预推免、夏令营、考研复试 / 实际考试年份 / 笔试、机试、面试**归档，三类考试在顶层完全分开。年份不连续或某类别缺失表示目前没有对应资料，不表示该年没有考试。

- “27届”暂映射为2026年考试、2027届，原始回忆未给考试日期，待核实；“26年复习资料”是汇编标题，不是所有题目的考试年份。
- 整理后的题目统一使用Markdown，保留表格、代码与题解；原文图片及图片形式的公式保留来源链接（需联网，原外链可能失效）。2026年机试逐题存放。
- 回忆、补编模拟题和备考指南均在文件中标注，不能等同于官方试卷；本次整理未逐题审校或执行参考代码。
- [原始离线完整版](原始资料/26年同济CS预推免复习资料_离线完整版.html)保留全部96篇资料；其余通用课程讲义继续在完整版中查阅。
- [原始机试图片（年份未确认）](原始资料/机试.jpg)、[原始文件校验值](原始资料/SHA256.json)、[来源索引](来源索引.json)、[网络补充](网络补充.md)。
- 原作者署名、来源链接和版权声明以原始资料为准。本仓库仅完成本地整理。

## 目录

'''
for event in ['预推免','夏令营','考研复试','通用复习']:
    intro+=f'### {event}\n\n'
    files = sorted((ROOT/event).rglob('*'))
    for p in files:
        if p.is_file() and p.suffix == ".md":
            label = p.relative_to(ROOT/event).as_posix()
            intro+=f'- [{label}]({p.relative_to(ROOT).as_posix()})\n'
    intro+='\n'
intro+='## 维护\n\n`python -m pip install -r 工具/requirements.txt` 安装转换依赖后，`python 工具/整理资料.py` 可重新生成拆分文件和目录；请在原始资料之外的笔记文件中记录自己的解答，避免被重建覆盖。网络补充为人工核对摘要，脚本不会覆盖。\n'
write('README.md',intro)
write('原始资料/README.md','# 原始资料\n\n五个用户文件按原字节保留，校验值见SHA256.json。机试.jpg未确认所属年份，不据文件名猜测归属。离线HTML中的外部附件链接不代表附件已下载；原有缺图或外链失效不由本次拆分修复。\n')
print(f'生成 {len(records)} 个Markdown文件，6个2026年Markdown文件，已保留5个原始文件。')
