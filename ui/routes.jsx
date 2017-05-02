import React from 'react';
import { browserHistory, IndexRedirect, Route, Router } from 'react-router';

import App from './components/app';
import PolicyContainer from './components/policies/container';
import AsyncLookupSearch, { redirectIfMatched } from './components/lookup-search';

// Trigger DAP pageviews when our history changes (for single-page-app users)
if (browserHistory && typeof gas !== 'undefined') {
  browserHistory.listen((loc) => {
    // Provided by DAP
    /* eslint-disable no-undef */
    gas('send', 'pageview', `${loc.pathname}${loc.search}`);
    /* eslint-enable no-undef */
  });
}

export default <Router history={browserHistory} >
  <Route path="/" component={App}>
    <IndexRedirect to="/requirements" />
    <Route path="search-redirect">
      <Route path="topics" component={AsyncLookupSearch} onEnter={redirectIfMatched} />
      <Route path="policies" component={AsyncLookupSearch} onEnter={redirectIfMatched} />
    </Route>
    <Route path="policies" component={PolicyContainer} />
  </Route>
</Router>;
