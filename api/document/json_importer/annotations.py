from collections import defaultdict
from typing import Callable, DefaultDict, Dict, Iterator, List, Tuple, Type

from document.models import Annotation, ExternalLink, FootnoteCitation
from document.tree import JSONAwareCursor, JsonDict

Annotator = Callable[
    [JSONAwareCursor, JsonDict, int],
    Annotation
]

annotators: Dict[str, Annotator] = {}


def annotator(fn: Annotator):
    annotators[fn.__name__] = fn
    return fn


@annotator
def footnote_citation(cursor: JSONAwareCursor, content: JsonDict,
                      start: int) -> FootnoteCitation:
    text = get_content_text(content['inlines'])
    referencing = list(cursor.filter(
        lambda m: m.node_type == 'footnote'
        and m.type_emblem == text.strip()
    ))
    if not referencing:
        raise ValueError(f'unable to find footnote for citation {text}')
    return FootnoteCitation(
        doc_node=cursor.model, start=start, end=start + len(text),
        footnote_node=referencing[0].model,
    )


@annotator
def external_link(cursor: JSONAwareCursor, content: JsonDict,
                  start: int) -> ExternalLink:
    text = get_content_text(content['inlines'])
    return ExternalLink(
        doc_node=cursor.model, start=start,
        end=start + len(text), href=content['href']
    )


AnnotationDict = DefaultDict[Type[Annotation], List[Annotation]]


def find_annotations(items: List[JsonDict],
                     start: int=0) -> Iterator[Tuple[JsonDict, int]]:
    for content in items:
        if content['content_type'] == '__text__':
            start += len(content['text'])
        else:
            yield (content, start)
            for icontent, istart in find_annotations(content['inlines'],
                                                     start):
                yield (icontent, istart)
                start = istart


def derive_annotations(cursor: JSONAwareCursor) -> AnnotationDict:
    annotations: AnnotationDict = defaultdict(list)

    for content, start in find_annotations(cursor.json_content):
        content_type = content['content_type']
        if content_type not in annotators:
            raise ValueError(f"no annotator found for {content_type}")
        anno = annotators[content_type](cursor, content, start)
        annotations[anno.__class__].append(anno)

    for child_cursor in cursor.children():
        for cls, annos in derive_annotations(child_cursor).items():
            annotations[cls].extend(annos)

    return annotations


def get_content_text(content: List[JsonDict]):
    chunks = []
    for c in content:
        if c['content_type'] == '__text__':
            chunks.append(c['text'])
        else:
            chunks.append(get_content_text(c['inlines']))
    return ''.join(chunks)
