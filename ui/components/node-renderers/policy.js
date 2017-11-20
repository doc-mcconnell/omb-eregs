import PropTypes from 'prop-types';
import React from 'react';

import DocumentNode from '../../util/document-node';
import renderNode from '../../util/render-node';
import LabeledText from '../labeled-text';
import Link from '../link';
import Footnote from './footnote';
import From from './from';

function findNodeText(docNode, nodeType, modelValue) {
  const containingNode = docNode.firstWithNodeType(nodeType);
  if (containingNode && containingNode.text.length > 0) {
    return containingNode.text;
  }
  return modelValue;
}

function footnotes(footnoteList) {
  if (footnoteList.length === 0) {
    return null;
  }
  const rendered = footnoteList.map(fn => (
    <Footnote key={fn.identifier} docNode={fn} />
  ));
  return (
    <div className="bottom-footnotes">
      { rendered }
    </div>
  );
}


/* Root of a policy document */
export default function Policy({ docNode }) {
  const fromNode = docNode.firstWithNodeType('from');
  const policyMeta = docNode.meta.policy;
  return (
    <div className="node-policy" id={docNode.identifier}>
      <header className="document-header clearfix">
        <div className="bold">
          { findNodeText(docNode, 'policyNum', policyMeta.omb_policy_id) }
        </div>
        <div>{ findNodeText(docNode, 'policyTitle', '') }</div>
        <h2 className="h1 document-heading">
          { findNodeText(docNode, 'subject', policyMeta.title) }
        </h2>
        <div className="original-link-container">
          <Link className="original-link" href={policyMeta.original_url}>See original</Link>
        </div>
        { fromNode ? <From docNode={fromNode} /> : null }
        <LabeledText id="issuance" label="Issued on:">
          { findNodeText(docNode, 'published', policyMeta.issuance_pretty) }
        </LabeledText>
      </header>
      { docNode.children.map(renderNode) }
      { footnotes(docNode.meta.descendant_footnotes.map(f => new DocumentNode(f))) }
    </div>
  );
}
Policy.propTypes = {
  docNode: PropTypes.instanceOf(DocumentNode).isRequired,
};
