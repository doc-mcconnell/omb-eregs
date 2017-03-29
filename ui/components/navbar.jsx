import React from 'react';


const Navbar = () => (
  <div className="overflow-auto">
    <div className="flex items-center navbar">
      <img
        className="pl2 pr1"
        alt="US flag"
        width="50"
        height="50"
        src="/static/img/omb-logo.png"
      />
      <div className="navbar-title">
          OMB Policy
      </div>
    </div>
  </div>
);

export default Navbar;