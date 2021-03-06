import PropTypes from 'prop-types';
import React from 'react';

import DocumentNode from '../../../util/document-node';
import renderContents from '../../../util/render-contents';

/* We're assuming, for the time being, that all rows within a single table
 * have the same number of columns. */
function deriveColspan(docNode) {
  const thead = docNode.firstWithNodeType('thead');
  const tr = thead ? thead.firstWithNodeType('tr') : null;
  return tr ? tr.children.length : 1;
}

export default function Tfoot({ docNode }) {
  const footnotes = docNode.meta.descendantFootnotes.map(ft => (
    <div className="clearfix footnote" key={ft.identifier} id={`${ft.identifier}-table`}>
      <div className="footnote-marker">{ft.marker}</div>
      <div className="footnote-text">{ renderContents(ft.content) }</div>
    </div>
  ));
  if (footnotes.length === 0) {
    return null;
  }
  return (
    <tfoot>
      <tr>
        <td colSpan={deriveColspan(docNode)} className="table-footer">
          <h1 className="h4">Footnotes for table</h1>
          { footnotes }
        </td>
      </tr>
    </tfoot>
  );
}
Tfoot.propTypes = {
  docNode: PropTypes.instanceOf(DocumentNode).isRequired,
};
