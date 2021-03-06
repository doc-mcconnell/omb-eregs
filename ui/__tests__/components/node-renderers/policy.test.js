import { shallow } from 'enzyme';
import React from 'react';

import Policy from '../../../components/node-renderers/policy';
import DocumentNode from '../../../util/document-node';
import PolicyObj from '../../../util/policy';
import {
  itIncludesTheIdentifier,
  itRendersChildNodes,
} from '../../test-utils/node-renderers';

jest.mock('../../../util/render-node');

describe('<Policy />', () => {
  const meta = {
    descendant_footnotes: [],
    policy: new PolicyObj({
      issuance: '2003-03-03',
      omb_policy_id: 'M-44-55',
      original_url: 'http://example.com/thing.pdf',
      title: 'Magistrate',
    }),
  };
  itIncludesTheIdentifier(Policy, { meta });
  itRendersChildNodes(Policy, { meta });

  it('uses the policy for default text', () => {
    const result = shallow(<Policy docNode={new DocumentNode({ meta })} />);
    const text = result.text();
    expect(text).toMatch(/M-44-55/);
    expect(text).toMatch(/Magistrate/);

    expect(result.find('Link').first().prop('href')).toEqual(
      'http://example.com/thing.pdf');

    expect(result.find('From')).toHaveLength(0);

    const date = result.find('LabeledText').first();
    expect(date.prop('id')).toEqual('issuance');
    expect(date.prop('label')).toEqual('Issued on:');
    expect(date.children().text()).toEqual('March 3, 2003');
  });
  it('can grab text from subnodes', () => {
    const docNode = new DocumentNode({
      children: [
        { children: [], node_type: 'other', text: 'other-text' },
        { children: [], node_type: 'subject', text: 'subject-here' },
        { children: [], node_type: 'policyNum', text: 'some-m-number' },
        { children: [], node_type: 'published', text: 'some date here' },
        { children: [], node_type: 'policyTitle', text: 'a title!' },
        { children: [], marker: 'Stuff:', node_type: 'from', text: 'Someone' },
      ],
      meta,
    });

    const result = shallow(<Policy docNode={docNode} />);
    const text = result.text();
    expect(text).not.toMatch(/M-44-55/);
    expect(text).not.toMatch(/Magistrate/);
    expect(text).toMatch(/subject-here/);
    expect(text).toMatch(/some-m-number/);
    expect(text).toMatch(/a title!/);
    expect(text).not.toMatch(/other-text/); // not specifically searched for

    const from = result.find('From').first();
    expect(from.prop('docNode')).toEqual(docNode.children[5]);

    const date = result.find('LabeledText').first();
    expect(date.children().text()).toEqual('some date here');
  });
});
