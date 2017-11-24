import sys
import re
from textwrap import TextWrapper

from pdfminer import layout

from .document import OMBDocument, OMBFootnoteCitation, OMBFootnote
from . import util
from .fontsize import FontSize


NUMBER_RE = re.compile(r'[0-9]')

FOOTNOTE_RE = re.compile(r'([0-9]+) (.+)')


def find_citations(doc):
    citations = []
    for line in doc.lines:
        prev_paragraph_chars = ''
        curr_citation = []

        def add_citation():
            citation = OMBFootnoteCitation(
                int(''.join(curr_citation)),
                prev_paragraph_chars
            )
            for char in curr_citation:
                char.set_annotation(citation)
            citations.append(citation)

        for char in line:
            if char.fontsize.size < doc.paragraph_fontsize.size:
                if NUMBER_RE.match(char):
                    if prev_paragraph_chars:
                        curr_citation.append(char)
            elif curr_citation:
                add_citation()
                curr_citation = []
                prev_paragraph_chars = ''
            else:
                prev_paragraph_chars += char
        if curr_citation:
            add_citation()
    return citations


def find_footnotes(doc):
    footnotes = []
    curr_footnote = None

    def finish_footnote():
        nonlocal curr_footnote

        if curr_footnote:
            number, text, lines = curr_footnote
            footnote = OMBFootnote(number, text)
            for line in lines:
                line.set_annotation(footnote)
            footnotes.append(footnote)
        curr_footnote = None

    for line in doc.lines:
        big_chars = [
            char for char in line
            if char.fontsize.size >= doc.paragraph_fontsize.size
        ]
        if not big_chars:
            chars = str(line)
            match = FOOTNOTE_RE.match(chars)
            if match:
                finish_footnote()
                footnote, desc = match.groups()
                curr_footnote = [int(footnote), desc, [line]]
            elif curr_footnote:
                curr_footnote[1] += chars
                curr_footnote[2].append(line)
        else:
            finish_footnote()
    finish_footnote()
    return footnotes


def main(doc):
    print("Citations:")
    for c in find_citations(doc):
        preceding_words = ' '.join(c.preceding_text.split(' ')[-3:])
        print(f"  #{c.number} appears after the text '{preceding_words}'")

    indent = "    "
    wrapper = TextWrapper(initial_indent=indent, subsequent_indent=indent)

    print("\nFootnotes:")
    for f in find_footnotes(doc):
        print(f"  #{f.number}:")
        print('\n'.join(wrapper.wrap(f.text)))
        print()


if __name__ == "__main__":
    with open(sys.argv[1], 'rb') as infile:
        main(OMBDocument.from_file(infile))
