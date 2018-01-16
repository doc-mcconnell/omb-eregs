import { EditorView } from 'prosemirror-view';

import createEditorState from './create-editor-state';
import exampleDoc from './example-doc';

// We need to load our CSS via require() rather than import;
// using the latter raises errors about not being able to find
// the module.
//
// I *suspect* it is because ts-loader (the TypeScript plugin for
// webpack) probably loads import statements on its own,
// without going through webpack, and it doesn't know what to
// do with non-standard kinds of imports like CSS, so using require()
// likely bypasses TypeScript and goes straight to webpack, which
// deals with it correctly. I could be wrong, though. -AV
declare function require(path: string): null;

require('prosemirror-view/style/prosemirror.css');
require('prosemirror-menu/style/menu.css');

const EDITOR_ID = 'editor';

function getEl(id: string): Element {
  const el = document.getElementById(id);
  if (!el)
    throw new Error(`element with id '${id}' not found`);
  return el;
}

window.addEventListener('load', () => {
  const view = new EditorView(getEl(EDITOR_ID), {
    state: createEditorState(exampleDoc),
  });
});
