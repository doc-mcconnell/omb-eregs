import re

from .document import OMBParagraph

PARAGRAPH_END_RE = re.compile(r'.+\.\s*$')

MAX_INDENT = 48


def cull_footer(page):
    lines = page[:]
    to_remove = []
    for line in reversed(lines):
        if line.annotation or line.is_blank():
            to_remove.append(line)
        else:
            break
    for line in to_remove:
        lines.remove(line)
    return lines


def zip_with_next(seq):
    '''
    >>> list(zip_with_next([1, 2, 3]))
    [(1, 2), (2, 3), (3, None)]
    '''

    nexts = seq[1:] + [None]
    return zip(seq, nexts)


def is_line_indented(line, next_line, doc):
    if next_line is None or not next_line.is_left_edge_near(doc):
        return False
    return line.left_edge - doc.left_edge <= MAX_INDENT


def annotate_paragraphs(doc):
    doc.annotators.require('footnotes', 'page_numbers', 'headings')
    in_paragraph = False
    paragraph_id = 0
    paragraphs = {}
    for page in doc.pages:
        for line, next_line in zip_with_next(cull_footer(page)):
            if line.is_blank() or line.annotation is not None:
                in_paragraph = False
            elif line.annotation is None:
                might_be_paragraph = False
                if line.is_left_edge_near(doc):
                    might_be_paragraph = True
                elif is_line_indented(line, next_line, doc):
                    might_be_paragraph = True
                    in_paragraph = False
                if might_be_paragraph:
                    first_char = line[0]
                    if first_char.fontsize.is_near(doc.paragraph_fontsize):
                        if not in_paragraph:
                            in_paragraph = True
                            paragraph_id += 1
                            paragraphs[paragraph_id] = []
                        line.set_annotation(OMBParagraph(paragraph_id))
                        paragraphs[paragraph_id].append(line)
        if in_paragraph:
            if PARAGRAPH_END_RE.match(str(line)):
                in_paragraph = False
    return paragraphs
