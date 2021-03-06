from typing import List

from document.tree import PrimitiveDict


def text(value: str) -> PrimitiveDict:
    return {
        "content_type": "__text__",
        "text": value
    }


def external_link(href: str, inlines: List[PrimitiveDict]) -> PrimitiveDict:
    return {
        "content_type": "external_link",
        "href": href,
        "inlines": inlines,
    }


def para(content: List[PrimitiveDict],
         children: List[PrimitiveDict]=None) -> PrimitiveDict:
    return {
        "node_type": "para",
        "content": content,
        "children": children or [],
    }


def footnote_citation(inlines: List[PrimitiveDict]) -> PrimitiveDict:
    return {
        "content_type": 'footnote_citation',
        "inlines": inlines,
    }


def footnote(marker: int, content: List[PrimitiveDict],
             children: List[PrimitiveDict]=None) -> PrimitiveDict:
    return {
        "node_type": "footnote",
        "marker": str(marker),
        "type_emblem": str(marker),
        "content": content,
        "children": children or [],
    }


def cite(inlines: List[PrimitiveDict]) -> PrimitiveDict:
    return {
        "content_type": "cite",
        "inlines": inlines,
    }
