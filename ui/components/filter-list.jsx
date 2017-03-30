/**
 * A container for filters, which can be removed with a click. Currently
 * closely tied to Keywords, but can be generalized in the future
 **/
import React from 'react';
import { Link } from 'react-router';

import { apiParam } from './lookup-search';
import SearchAutocomplete from './search-autocomplete';

export function Filter({ existingIds, idToRemove, location, name, removeParam }) {
  const remainingIds = existingIds.filter(v => v !== idToRemove);
  const { pathname, query } = location;
  const modifiedQuery = Object.assign({}, query, {
    [removeParam]: remainingIds.join(','),
  });
  delete modifiedQuery.page;

  return (
    <li className="active-filter rounded clearfix mb1 flex relative">
      <span className="filter-name col col-9 p1 center">{name}</span>
      <Link
        to={{ pathname, query: modifiedQuery }}
        className="remove-filter-link rounded-right col col-3 p1 center flex absolute"
      >
        <span className="close-button center block">x</span>
      </Link>
    </li>
  );
}
Filter.defaultProps = {
  existingIds: [],
  idToRemove: 0,
  location: { pathname: '', query: {} },
  name: '',
  removeParam: '',
};
Filter.propTypes = {
  existingIds: React.PropTypes.arrayOf(React.PropTypes.number),
  idToRemove: React.PropTypes.number,
  location: React.PropTypes.shape({
    pathname: React.PropTypes.string,
    query: React.PropTypes.shape({}),
  }),
  name: React.PropTypes.string,
  removeParam: React.PropTypes.string,
};

/* Mapping between a lookup type (e.g. "keywords") and the query field that
 * this would need to modify to add/remove lookup values */
export const searchParam = {
  keywords: 'keywords__id__in',
  policies: 'policy_id__in',
};

export default function FilterList({ existingFilters, lookup, router }) {
  const filterIds = existingFilters.map(existing => existing.id);
  return (
    <div className="req-filter-ui my2">
      <div className="filter-section-header bold">
        {lookup.charAt(0).toUpperCase() + lookup.substr(1)}
      </div>
      <ol className="list-reset">
        { existingFilters.map(filter =>
          <Filter
            key={filter.id} existingIds={filterIds} idToRemove={filter.id}
            location={router.location} name={filter[apiParam[lookup]]}
            removeParam={searchParam[lookup]}
          />)}
      </ol>
      <SearchAutocomplete lookup={lookup} insertParam={searchParam[lookup]} router={router} />
    </div>
  );
}
FilterList.defaultProps = {
  existingFilters: [],
  lookup: 'keywords',
  router: { location: {} },
};
FilterList.propTypes = {
  existingFilters: React.PropTypes.arrayOf(React.PropTypes.shape({
    id: React.PropTypes.number,
  })),
  lookup: React.PropTypes.oneOf(Object.keys(searchParam)),
  router: React.PropTypes.shape({
    location: React.PropTypes.shape({}),
  }),
};
