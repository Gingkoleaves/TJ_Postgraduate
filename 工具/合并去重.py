"""合并推免目录与重复内容；只处理生成清单中的文件。"""
import re
import json
import os
from pathlib import Path


def clean(s):
    # 清理转换器重复产生的标题和来源行，不碰代码围栏。
    out=[];seen=set();fence=False;title=None
    for line in s.splitlines():
        if line.startswith('```'):fence=not fence
        if not fence and (line.startswith('原文：') or line.startswith('> ')):
            if line in seen:continue
            seen.add(line)
        if not fence and line.startswith('# '):
            if title is None:title=line[2:]
            elif line[2:]==title:continue
            else:line='#'+line
        if not fence and not line.strip():
            if not out or not out[-1].strip():continue
        out.append(line)
    return '\n'.join(out).strip()+'\n'


def body(s):
    return re.sub(r'^# [^\n]*\n\s*','',s,count=1).strip()


def relocate(s, old, new):
    def link(m):
        dest=m[1]; bracket=dest.startswith('<');dest=dest.strip('<>')
        if '://' in dest or dest.startswith('#'):return m[0]
        path,sep,anchor=dest.partition('#')
        target=os.path.normpath(str(Path(old).parent/path))
        rel=Path(os.path.relpath(target,Path(new).parent)).as_posix()
        return '](<'+rel+(sep+anchor if sep else '')+'>)'
    return re.sub(r'\]\((<[^>]+>|[^)]+)\)',link,s)


def finalize(root, docs, records):
    moved={};related={};log=[]
    for path,s in json.loads((root/'工具/网络补充原文.json').read_text(encoding='utf-8')).items():
        docs['推免/'+path.split('/',1)[1]]=s
    for p in list(docs):docs[p]=clean(docs[p])

    def merge(target, paths, labels=None):
        parts=['# '+Path(target).stem]
        for i,p in enumerate(paths):
            parts.extend(['## '+(labels[i] if labels else Path(p).stem),relocate(body(docs.pop(p)),p,target)])
            moved[p]=target
        docs[target]='\n\n'.join(parts)+'\n'
        log.append(f'合并 {len(paths)} 份 → `{target}`')

    # 去重已确认相同的炸飞机题：代码去掉注释和空白后相同。
    a='推免/2020/机试/夏令营-题目与解析.md';b='考研复试/2023/机试/考研复试-题目与解析.md'
    ma=re.search(r'^## 第四题：算法——炸飞机游戏.*?(?=^## 总结)',docs[a],re.M|re.S)
    mb=re.search(r'^### 第三题：炸飞机游戏.*',docs[b],re.M|re.S)
    assert ma and mb
    target='通用复习/机试/炸飞机游戏.md'
    shared=ma[0]
    docs[target]='# 炸飞机游戏\n\n来源：离线汇编 [2020夏令营 s30](../../原始资料/26年同济CS预推免复习资料_离线完整版.html#s30) 与 [2023考研复试 s29](../../原始资料/26年同济CS预推免复习资料_离线完整版.html#s29)。两份整理题干相同，代码忽略注释和空白后相同；仅保留详细版本。年份归属沿用资料，未独立确认。\n\n'+shared
    for p,m in [(a,ma),(b,mb)]:
        label=m[0].splitlines()[0]
        docs[p]=docs[p][:m.start()]+label+'\n\n完整题干和题解见[炸飞机游戏](../../../通用复习/机试/炸飞机游戏.md)。原资料的年份、分值标注仍保留。\n\n'+docs[p][m.end():]
        related[p]=[target]
    log.append('炸飞机游戏：合并相同题干和代码为通用题，各年份保留索引。')

    # 将2025夏令营通用备考内容收拢；当年考情保留在年份目录。
    summer='推免/2025/面试/夏令营-回忆与复习资料.md'
    generic='通用复习/面试/同济CS历年面试真题分类整理（附参考回答）.md'
    target='通用复习/面试/面试题库与备考.md'
    s=docs[summer]
    starts=list(re.finditer(r'^## \*\*([一二三四五六七])、.*$',s,re.M))
    assert len(starts)==7
    sections={m[1]:s[m.start():starts[i+1].start() if i+1<len(starts) else len(s)] for i,m in enumerate(starts)}
    common=docs.pop(generic)
    # 同题短答案以详细答案为准，保留问题和出现年份并链接。
    pairs=[('什么是数据相关', '5.1'),('怎么解决CPU分支','5.2'),('计算机组成原理和计算机系统结构','5.8'),('介绍MCTS','5.3'),('多模态融合存在哪些问题','5.4'),('多模态融合的研究与实际应用','5.5'),('你怎么理解词嵌入','5.6'),('文本和图像的特征','5.7'),('介绍一下LoRA','5.9')]
    for key,anchor in pairs:
        pattern=r'(^#### [^\n]*'+re.escape(key)+r'[^\n]*\n).*?(?=^#{2,4} |\Z)'
        common,n=re.subn(pattern,lambda m:m[1]+'\n见[详细知识点与回答](#tech-'+anchor.replace('.','-')+')。\n\n',common,flags=re.M|re.S)
        assert n==1,(key,n)
    detail=sections['五']
    detail=re.sub(r'^(###? \*\*(5\.\d+)[^\n]*$)',lambda m:'<a id="tech-'+m[2].replace('.','-')+'"></a>\n\n'+m[1],detail,flags=re.M)
    # PPT时间分配、专业详细推导属于补充；重复问答/准备清单以通用版为准。
    extras=sections['二']+'\n\n'+detail
    project=re.search(r'^###? \*\*6\.2.*?(?=^###? \*\*6\.3)',sections['六'],re.M|re.S)
    if project:extras+='\n\n'+project[0]
    docs[target]='# 面试题库与备考\n\n合并历年分类题库与2025夏令营备考指南。共同的英语、思政、项目问答和准备清单只保留分类版；专业题链接到详细回答。不同年份流程仍以各年份回忆为准。原始完整版本可由来源链接核对。\n\n'+body(common)+'\n\n## 补充讲解（2025夏令营备考指南）\n\n来源：[原始 s22](../../原始资料/26年同济CS预推免复习资料_离线完整版.html#s22)。\n\n'+relocate(extras,summer,target)
    docs[summer]=s[:starts[1].start()]+'\n\n通用问答、PPT准备和专业课详解合并至[面试题库与备考](../../../通用复习/面试/面试题库与备考.md)。\n'
    moved[generic]=target;related[summer]=[target]
    log.append('面试：共同英语/思政/项目问答和准备清单归入统一题库，9道专业问题共用详细回答；年份考情保留。')

    # 同年份同考核的短回忆、网络摘要合为一份，保留来源分节。
    for year in ['2023','2024','2025']:
        for typ in ['笔试','机试','面试']:
            folder=f'推免/{year}/{typ}/'
            paths=[p for p in docs if p.startswith(folder) and '补编' not in p and not re.search(r'预推免-\d',Path(p).name)]
            if len(paths)>1:merge(folder+'考题与回忆汇总.md',sorted(paths))
    paths=sorted(p for p in docs if p.startswith('推免/2024/笔试/预推免-补编'))
    merge('推免/2024/笔试/补编练习与解析.md',paths)
    # 只有两个附件链接的文件并入通用题库，不保留单独入口。
    attachment='通用复习/面试/同济大学计算机面试题库.md'
    docs[target]+='\n\n## 外部附件索引\n\n'+body(docs.pop(attachment));moved[attachment]=target
    log.append('将7份2024补编资料合为一份；只有附件链接的面试题库并入统一面试资料。')

    def final(p):
        while p in moved:p=moved[p]
        return p
    # 修复所有内部链接；跨文件合并后的相对路径已经由relocate调整。
    for p,s in list(docs.items()):
        def fix(m):
            dest=m[1].strip('<>')
            if '://' in dest or dest.startswith('#'):return m[0]
            q,sep,anchor=dest.partition('#')
            resolved=Path(os.path.normpath(str(Path(p).parent/q))).as_posix()
            resolved=final(resolved)
            rel=Path(os.path.relpath(resolved,Path(p).parent)).as_posix()
            return '](<'+rel+(sep+anchor if sep else '')+'>)'
        docs[p]=re.sub(r'\]\((<[^>]+>|[^)]+)\)',fix,s)
    for row in records:
        old=row['path'];row['path']=final(old)
        if old in related:row['related_paths']=[final(q) for q in related[old]]
    docs['合并说明.md']='# 合并与去重记录\n\n预推免与夏令营统一为 `推免/年份/笔试、机试、面试`，来源类别通过文件名或分节标注。考研复试继续独立。\n\n'+''.join('- '+x+'\n' for x in log)+'\n同名数独、文件处理、二分输出等题目的输入输出或版本不同，保留各版本；知识点相同不视为同一题。常考英文问题包含额外练习，仍单独保留。所有原始资料和历史提交保留。\n'
    docs['网络补充.md']='# 网络补充记录\n\n检索日期：2026-09-14。三份摘要已并入[2023笔试](推免/2023/笔试/考题与回忆汇总.md)和[2023机试](推免/2023/机试/考题与回忆汇总.md)，保留原来源链接、学院和考核类别。原文摘要由 `工具/网络补充原文.json` 保存以便重建。\n'
    for p in docs:docs[p]=clean(docs[p])
    return docs,records
