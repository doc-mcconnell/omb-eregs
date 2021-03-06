import PropTypes from 'prop-types';
import React from 'react';

import PagersContainer from '../pagers';
import Policy from '../../util/policy';
import PolicyView from './policy-view';
import ThingCounterContainer from '../thing-counters';

export default function PoliciesView({ policies, count, topicsIds }) {
  const singular = 'policy';
  const plural = 'policies';

  return [
    <ThingCounterContainer count={count} key="counter" singular={singular} plural={plural} />,
    <ul className="policy-list list-reset" key="policy-list">
      { policies.map(policy =>
        <PolicyView key={policy.id} policy={policy} topicsIds={topicsIds} />,
      )}
    </ul>,
    <PagersContainer count={count} key="pager" route="policies" />,
  ];
}
PoliciesView.propTypes = {
  policies: PropTypes.arrayOf(PropTypes.instanceOf(Policy)),
  count: PropTypes.number,
  topicsIds: PropTypes.string,
};
PoliciesView.defaultProps = {
  policies: [],
  count: 0,
  topicsIds: '',
};
