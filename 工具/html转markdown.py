"""将题库 HTML 转为 Markdown；依赖 lxml，代码块原样保留。"""
import re
from lxml import html


def plain(value):
    value = re.sub(r'\s+', ' ', value or '')
    return re.sub(r'([\\`*_\[\]<>])', r'\\\1', value)


def convert_html(source):
    tree = html.fromstring(source)

    def children(e):
        return plain(e.text) + ''.join(render(c) + plain(c.tail) for c in e)

    def render(e):
        tag = e.tag
        if not isinstance(tag, str) or tag in ('head', 'style', 'script'):
            return ''
        if tag == 'pre':
            value = ''.join(e.itertext()).replace('\r\n', '\n')
            fence = '`' * max(3, max((len(x) + 1 for x in re.findall(r'`+', value)), default=3))
            lang = 'cpp' if '#include' in value else 'text'
            return '\n\n' + fence + lang + '\n' + value.rstrip('\n') + '\n' + fence + '\n\n'
        if tag == 'code':
            value = ''.join(e.itertext())
            fence = '`' * max(1, max((len(x) + 1 for x in re.findall(r'`+', value)), default=1))
            pad = ' ' if '`' in value or value.startswith(' ') or value.endswith(' ') else ''
            return fence + pad + value + pad + fence
        if tag == 'img':
            return '![' + plain(e.get('alt') or '原文图片') + '](<' + e.get('src', '') + '>)'
        if tag == 'br':
            return '\n'
        if tag == 'hr':
            return '\n\n---\n\n'
        if tag == 'table':
            rows = []
            for row in e.xpath('.//tr'):
                cells = [children(c).strip().replace('|', '&#124;').replace('\n', '<br>') for c in row if c.tag in ('th', 'td')]
                if cells:
                    rows.append(cells)
            if not rows:
                return ''
            width = max(map(len, rows))
            rows = [r + [''] * (width - len(r)) for r in rows]
            lines = ['| ' + ' | '.join(r) + ' |' for r in rows]
            lines.insert(1, '| ' + ' | '.join(['---'] * width) + ' |')
            return '\n\n' + '\n'.join(lines) + '\n\n'
        if tag in ('ul', 'ol'):
            rows = []
            for i, li in enumerate(e):
                if li.tag != 'li':
                    continue
                value = children(li).strip()
                prefix = f'{i + int(e.get("start", "1"))}. ' if tag == 'ol' else '- '
                lines = value.splitlines()
                rows.append(prefix + ('\n' + ' ' * len(prefix)).join(lines))
            return '\n\n' + '\n'.join(rows) + '\n\n'
        value = children(e)
        if tag == 'a':
            href = e.get('href')
            return '[' + value.strip() + '](<' + href + '>)' if href else value
        if tag in ('strong', 'b', 'em', 'i'):
            mark = '**' if tag in ('strong', 'b') else '*'
            return mark + value.strip() + mark if value.strip() else ''
        if re.fullmatch(r'h[1-6]', tag):
            return '\n\n' + '#' * int(tag[1]) + ' ' + value.strip() + '\n\n'
        if tag == 'blockquote' or (tag == 'div' and e.get('class') == 'archive-note'):
            return '\n\n' + '\n'.join('> ' + line for line in value.strip().splitlines()) + '\n\n'
        if tag in ('sup', 'sub'):
            return '<' + tag + '>' + value + '</' + tag + '>'
        if tag in ('p', 'div', 'article', 'section', 'main'):
            return '\n\n' + value.strip() + '\n\n'
        return value

    # 逐行处理，代码围栏内的空白与缩进不动。
    output = []
    fence = None
    for line in render(tree).strip().splitlines():
        marker = re.match(r"^(`{3,})", line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif line.strip() == fence:
                fence = None
            output.append(line)
        elif fence is not None:
            output.append(line)
        elif not line.strip():
            if output and output[-1] != "":
                output.append("")
        else:
            output.append(line.rstrip())
    title = tree.findtext('.//title')
    prefix = '# ' + plain(title) + '\n\n' if title else ''
    return prefix + '\n'.join(output).strip() + '\n'
