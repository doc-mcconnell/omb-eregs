import {
  baseKeymap,
  chainCommands,
  deleteSelection,
  selectNodeBackward,
  selectNodeForward,
} from 'prosemirror-commands';
import { undo, redo } from 'prosemirror-history';
import { keymap } from 'prosemirror-keymap';

import { JsonApi } from './Api';
import { addListItem, makeSave } from './commands';
import schema from './schema';

// Removing joinBackwards/forwards from actions taken when deleting as they
// need to be tuned a bit better to our use case.
const backspace = chainCommands(deleteSelection, selectNodeBackward);
const del = chainCommands(deleteSelection, selectNodeForward);

// Similarly, removing the default "Enter" behavior (newlineInCode,
// createParagraphNear, liftEmptyBlock, splitBlock) for the same reason.
const enter = addListItem;

export default function menu(api: JsonApi) {
  return keymap({
    ...baseKeymap,
    'Backspace': backspace,
    'Mod-Backspace': backspace,
    'Delete': del,
    'Mod-Delete': del,
    'Mod-z': undo,
    'Shift-Mod-z': redo,
    'Mod-s': makeSave(api),
    'Enter': enter,
    // Macs have additional keyboard combinations for deletion; we set them
    // for all OSes as a convenience
    'Ctrl-h': backspace,
    'ALt-Backspace': backspace,
    'Ctrl-d': del,
    'Ctrl-Alt-Backspace': del,
    'Alt-Delete': del,
    'Alt-d': del,
  });
}
