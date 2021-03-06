from decimal import Decimal
from html import escape


def to_px_style_attr(**kwargs):
    '''
    >>> to_px_style_attr(width=50.12345, height=40.65321)
    'style="height: 40.65px; width: 50.12px"'
    '''

    props = []
    for name, val in kwargs.items():
        val = Decimal(val).quantize(Decimal('.01'))
        props.append(f'{name}: {val}px')
    props.sort()
    css = '; '.join(props)
    return f'style="{css}"'


def to_html(doc):
    doc.annotators.require_all()
    chunks = []
    legend = set()
    for page in doc.pages:
        pagestyle = to_px_style_attr(width=page.ltpage.width,
                                     height=page.ltpage.height)
        chunks.append(
            f'<h2 id="{page.number}">'
            f'<a href="#{page.number}">Page {page.number}</a></h2>'
        )
        chunks.append(f'<div class="page" data-page="{page.number}" '
                      f'{pagestyle}>\n')
        for line, lineno in zip(page, range(1, len(page) + 1)):
            line_classes = ['line']
            if line.annotation is not None:
                classname = line.annotation.__class__.__name__
                cssname = f'line-{classname}'
                line_classes.append(cssname)
                legend.add((classname, cssname))
            line_classes_str = ' '.join(line_classes)
            chunks.append(f'<div class="{line_classes_str}" '
                          f'data-anno="{escape(str(line.annotation))}"'
                          f'data-lineno="{lineno}">\n')
            for char in line:
                charstyle = to_px_style_attr(
                    top=page.ltpage.height - char.ltchar.y1,
                    left=char.ltchar.x0,
                    width=char.ltchar.width,
                    height=char.ltchar.height,
                )
                chunks.append(f'<div class="char" {charstyle}>{char}</div>\n')
            chunks.append(f'</div>')
        chunks.append(f'</div>\n')

    return (''.join(chunks), {'legend': legend})
