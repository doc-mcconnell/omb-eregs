import PropTypes from 'prop-types';
import React from 'react';

import { Link } from '../../routes';

export default function PolicyLink({ policy }) {
  return (
    <div className="policy-title metadata">
      Policy title:{' '}
      <Link route="policies" params={{ id__in: policy.id }}>
        <a>{policy.title_with_number}</a>
      </Link>
    </div>
  );
}

PolicyLink.propTypes = {
  policy: PropTypes.shape({
    id: PropTypes.number,
    title_with_number: PropTypes.string,
  }).isRequired,
};
