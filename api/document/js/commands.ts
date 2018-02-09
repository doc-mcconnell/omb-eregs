import { Node, ResolvedPos } from 'prosemirror-model';
import { TextSelection } from 'prosemirror-state';

import { JsonApi } from './Api';
import { deeperBullet, renumberList } from './list-utils';
import pathToResolvedPos, { SelectionPath } from './path-to-resolved-pos';
import schema, { factory } from './schema';
import serializeDoc from './serialize-doc';
import { walkUpUntil } from './util';

function safeDocCheck(doc: Node) {
  try {
    doc.check();
  } catch (e) {
    console.error('Doc no longer valid', e);
  }
}

// Append the provided element at the closest valid point after the user's
// cursor/"head" of the current selection. Then, move the cursor to select
// that element.
export function appendNearBlock(state, dispatch, element: Node, selectionPath: SelectionPath) {
  // Checking whether or not this action is possible
  if (!dispatch) {
    return true;
  }
  const pos = state.selection.$head;
  // Walk up the document until we hit a "block" element. We'll assume that
  // if there's one, there can be many (including a new para).
  const blockDepth = walkUpUntil(pos, node => node.type.spec.group === 'block');
  if (blockDepth >= 0) {
    const insertPos = pos.after(blockDepth);
    let tr = state.tr.insert(insertPos, element);
    const eltStart = pathToResolvedPos(
      tr.doc.resolve(insertPos + 1),
      selectionPath,
    );
    const eltEnd = eltStart.pos + eltStart.parent.nodeSize - 1; // inclusive
    tr = tr.setSelection(TextSelection.create(
      tr.doc,
      eltStart.pos,
      eltEnd,
    ));
    dispatch(tr.scrollIntoView());
    safeDocCheck(tr.doc);
  }

  return true;
}

export function appendParagraphNear(state, dispatch) {
  const element = factory.para(' ');
  return appendNearBlock(state, dispatch, element, ['inline']);
}

export function appendBulletListNear(state, dispatch) {
  const element = factory.list([
    factory.listitem(deeperBullet(state.selection.$head), [factory.para(' ')]),
  ]);
  return appendNearBlock(state, dispatch, element, ['listitem', 'para', 'inline']);
}

export function makeSave(api: JsonApi) {
  return async state => api.write(serializeDoc(state.doc));
}

export function makeSaveThenXml(api: JsonApi) {
  return async (state) => {
    await api.write(serializeDoc(state.doc));
    window.location.assign(`${window.location.href}/akn`);
  };
}

const inLi = (pos: ResolvedPos) => (
  pos.depth >= 3
  && pos.node(pos.depth).type === schema.nodes.inline
  && pos.node(pos.depth - 1).type === schema.nodes.para
  && pos.node(pos.depth - 2).type === schema.nodes.listitem
  && pos.node(pos.depth - 3).type === schema.nodes.list
);
const atEndOfLi = (pos: ResolvedPos) => (
  pos.depth >= 2
  && pos.pos === pos.end(pos.depth)
  && pos.pos === pos.end(pos.depth - 1) - 1
  && pos.pos === pos.end(pos.depth - 2) - 2
);

export function addListItem(state, dispatch?) {
  const pos = state.selection.$head;
  if (!inLi(pos) || !atEndOfLi(pos)) {
    return false;
  }
  if (!dispatch) {
    return true;
  }

  const endOfLi: number = pos.end(pos.depth - 2);
  const insertPos = endOfLi + 1;
  // This marker will be replaced during the renumber step
  const liToInsert = factory.listitem('', [factory.para(' ')]);
  let tr = state.tr.insert(insertPos, liToInsert);
  tr = renumberList(tr, insertPos);
  const cursorStart = pathToResolvedPos(
    tr.doc.resolve(insertPos + 1),
    ['para', 'inline'],
  ).pos;
  tr = tr.setSelection(TextSelection.create(
    tr.doc,
    cursorStart,
    cursorStart + 1, // select the space
  ));
  tr = tr.scrollIntoView();
  dispatch(tr);
  return true;
}
