jest.mock('../Api');
jest.mock('../serialize-doc');
window.location.assign = jest.fn();

import { EditorState, TextSelection } from 'prosemirror-state';

import Api from '../Api';
import {
  appendBulletListNear,
  appendNearBlock,
  appendParagraphNear,
  makeSave,
  makeSaveThenXml,
} from '../commands';
import schema, { factory } from '../schema';
import serializeDoc from '../serialize-doc';
import pathToResolvedPos, { NthType } from '../path-to-resolved-pos';

function executeTransform(initialState: EditorState, transform): EditorState {
  const dispatch = jest.fn();

  transform(initialState, dispatch);
  const transaction = dispatch.mock.calls[0][0];
  return initialState.apply(transaction);
}


describe('appendNearBlock()', () => {
  const paraTransform = (state, dispatch) =>
    appendNearBlock(state, dispatch, factory.para(' '), ['inline']);

  it('adds a node after the current', () => {
    const doc = factory.policy([
      factory.para('aaa'),
      factory.para('bbb'),
      factory.para('ccc'),
    ]);
    const selection = new TextSelection(pathToResolvedPos(
      doc,
      // Inside the 'bbb' paragraph
      [new NthType(1, 'para'), 'inline', 'b'.length],
    ));
    const state = EditorState.create({ doc, selection });
    const modifiedDoc = executeTransform(state, paraTransform).doc;

    expect(modifiedDoc.content.childCount).toBe(4);
    const texts: string[] = [];
    modifiedDoc.content.forEach((child) => {
      expect(child.type).toBe(schema.nodes.para);
      texts.push(child.textContent);
    });
    expect(texts).toEqual(['aaa', 'bbb', ' ', 'ccc']);
  });

  it('inserts at the right layer of nesting', () => {
    const doc = factory.policy([
      factory.para('aaa', [
        factory.para('subpar'),
        factory.unimplementedNode({}),
      ]),
    ]);
    const selection = new TextSelection(pathToResolvedPos(
      doc,
      // Inside the 'subpar' paragraph
      ['para', 'para', 'inline', 'sub'.length],
    ));
    const state = EditorState.create({ doc, selection });
    const modifiedDoc = executeTransform(state, paraTransform).doc;

    expect(modifiedDoc.content.childCount).toBe(1);
    const parA = modifiedDoc.content.child(0);
    expect(parA.content.childCount).toBe(4); // inline + 3 children
    expect(parA.content.child(2).textContent).toBe(' ');
  });

  it('skips over children', () => {
    const doc = factory.policy([
      factory.para('aaa', [
        factory.para('subpar'),
        factory.unimplementedNode({}),
      ]),
    ]);
    const selection = new TextSelection(pathToResolvedPos(
      doc,
      // Inside the 'aaa' paragraph
      ['para', 'inline', 'a'.length],
    ));
    const state = EditorState.create({ doc, selection });
    const modifiedDoc = executeTransform(state, paraTransform).doc;

    expect(modifiedDoc.content.childCount).toBe(2);
    expect(modifiedDoc.content.child(1).textContent).toBe(' ');
  });
});

describe('appendParagraphNear()', () => {
  const doc = factory.policy([factory.para('aaa')]);
  const selection = new TextSelection(pathToResolvedPos(
    doc,
    ['para', 'inline', 'a'.length],
  ));
  const state = EditorState.create({ doc, selection });
  const modified = executeTransform(state, appendParagraphNear);

  it('adds a paragraph', () => {
    expect(modified.doc.content.childCount).toBe(2);
    const texts: string[] = [];
    modified.doc.content.forEach((child) => {
      expect(child.type).toBe(schema.nodes.para);
      texts.push(child.textContent);
    });
    expect(texts).toEqual(['aaa', ' ']);
  });

  it('puts the cursor in the right place', () => {
    const resolvedPos = modified.selection.$anchor;
    expect(resolvedPos.depth).toBe(2);  // 0: policy, 1: para, 2: inline
    expect(resolvedPos.parent.type).toBe(schema.nodes.inline);
    expect(resolvedPos.parent).toBe(
      modified.doc.content.child(1).content.child(0));
  });
});

describe('appendBulletListNear()', () => {
  const doc = factory.policy([factory.para('aaa')]);
  const selection = new TextSelection(pathToResolvedPos(
    doc,
    ['para', 'inline', 'a'.length],
  ));
  const state = EditorState.create({ doc, selection });
  const modified = executeTransform(state, appendBulletListNear);

  it('adds a list, listitem, and para', () => {
    expect(modified.doc.content.childCount).toBe(2);

    const list = modified.doc.content.child(1);
    expect(list.type).toBe(schema.nodes.list);
    expect(list.content.childCount).toBe(1);

    const li = list.content.child(0);
    expect(li.type).toBe(schema.nodes.listitem);
    expect(li.content.childCount).toBe(1);

    const para = li.content.child(0);
    expect(para.type).toBe(schema.nodes.para);
    expect(para.textContent).toBe(' ');
  });

  it('puts the cursor in the right place', () => {
    const resolvedPos = modified.selection.$anchor;
    // 0: policy, 1: list, 2: listitem, 3: para, 4: inline
    expect(resolvedPos.depth).toBe(4);
    expect(resolvedPos.parent.type).toBe(schema.nodes.inline);
    expect(resolvedPos.parent).toBe(
      modified.doc.content.child(1).content.child(0).content.child(0).content.child(0));
  });
});

describe('makeSave()', () => {
  it('calls the save function', async () => {
    (serializeDoc as jest.Mock).mockImplementationOnce(() => ({ serialized: 'content' }));

    const api = new Api({ contentType: 'json', csrfToken: '', url: '' });
    const save = makeSave(api);
    await save({ doc: 'stuff' });

    expect(serializeDoc).toBeCalledWith('stuff');
    expect(api.write).toBeCalledWith({ serialized: 'content' });
  });
});

describe('makeSaveThenXml()', () => {
  it('calls the save function', async () => {
    (serializeDoc as jest.Mock).mockImplementationOnce(() => ({ serialized: 'content' }));

    const api = new Api({ contentType: 'json', csrfToken: '', url: '' });
    const save = makeSaveThenXml(api);
    await save({ doc: 'stuff' });

    expect(serializeDoc).toBeCalledWith('stuff');
    expect(api.write).toBeCalledWith({ serialized: 'content' });
  });

  it('changes the window location', async () => {
    const locationAssign = window.location.assign as jest.Mock;
    locationAssign.mockClear();

    const api = new Api({ contentType: 'json', csrfToken: '', url: '' });
    const save = makeSaveThenXml(api);
    await save({ doc: 'stuff' });

    const param = locationAssign.mock.calls[0][0];
    expect(param).toMatch(/akn$/);
  });
});
