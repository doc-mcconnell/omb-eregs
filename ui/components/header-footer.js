import Head from 'next/head';
import PropTypes from 'prop-types';
import React from 'react';

import Disclaimer from './disclaimer';
import Navbar from './navbar';
import Footer from './footer';

import pageTitle from '../util/page-title';


/* Generates the myriad tags needed to support favicons across a variety of
 * OSes, browsers, and display sizes. */
function faviconTags() {
  const appleSizes = [57, 60, 72, 76, 114, 120, 144, 152];
  const appleIcons = appleSizes.map(number =>
    (
      <link
        key={number}
        rel="apple-touch-icon-precomposed"
        sizes={`${number}x${number}`}
        href={`/static/img/favicon/apple-icon-${number}x${number}.png`}
      />
    ),
  );
  const iconSizes = [16, 32, 96, 128, 196];
  const icons = iconSizes.map(number =>
    (
      <link
        key={number}
        rel="icon"
        type="img/png"
        sizes={`${number}x${number}`}
        href={`/static/img/favicon/favicon-${number}x${number}.png`}
      />
    ),
  );

  const msSizes = [70, 144, 150, 310];
  const msSquares = msSizes.map(number =>
    (
      <meta
        key={number}
        name={`msapplication-square${number}x${number}logo`}
        content={`/static/img/favicon/mstile-${number}x${number}.png`}
      />
    ),
  );

  return ([
    appleIcons,
    icons,
    <meta key="appName" name="application-name" content="OMB Policy Library (Beta)" />,
    <meta key="tileColor" name="msapplication-TileColor" content="#FFFFFF" />,
    <meta
      key="tileImage"
      name="msapplication-TileImage"
      content="/static/img/favicon/mstile-144x144.png"
    />,
    msSquares,
    <meta
      key="mstile"
      name="msapplication-wide310x150logo"
      content="/static/img/favicon/mstile-310x150.png"
    />,
  ]);
}

export default function HeaderFooter({ children, showSearch, wrapperClassName }) {
  const klasses = ['container', wrapperClassName].join(' ');

  return (
    <React.Fragment>
      <Head>
        <link rel="stylesheet" href="/static/styles.css" />
        <script
          async
          type="text/javascript"
          id="_fed_an_ua_tag"
          src="https://dap.digitalgov.gov/Universal­Federated­Analytics­Min.js?agency=EOP&subagency=OMB"
        />
        { faviconTags() }
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      {
        /* Set a default page title. This can be overridden if pageTitle()
          is also called in child components */
        pageTitle()
      }
      <div className="page-header-wrapper">
        <Disclaimer key="disclaimer" />
        <Navbar key="navbar" showSearch={showSearch} />
      </div>
      <div className={klasses}>{children}</div>
      <Footer />
      <script src="/static/ie.js" />
    </React.Fragment>
  );
}

HeaderFooter.propTypes = {
  showSearch: PropTypes.bool,
  wrapperClassName: PropTypes.string,
  children: PropTypes.node.isRequired,
};

HeaderFooter.defaultProps = {
  showSearch: true,
  wrapperClassName: '',
};
