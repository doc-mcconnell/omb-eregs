import { shallow } from 'enzyme';
import React from 'react';

import TopicLink from '../../../components/requirements/topic-link';

describe('<TopicLink />', () => {
  let topic = { id: 1, name: 'hello link 1' };
  const basic = shallow(
    <TopicLink topic={topic} />,
  );
  it('renders', () => {
    expect(basic.type()).toBe('li');
  });
  it('has the right route', () => {
    expect(basic.find('Link').prop('route')).toMatch('requirements');
  });
  it('has the right text content', () => {
    expect(basic.find('Link').children().text()).toMatch('hello link 1');
  });

  topic = { id: 2, name: 'hello link 2', route: 'policies' };
  const definedRoute = shallow(
    <TopicLink topic={topic} />,
  );
  it('has the correct route', () => {
    expect(definedRoute.find('Link').prop('route')).toMatch('policies');
  });
  it('has the new content values', () => {
    expect(definedRoute.find('Link').children().text()).toMatch('hello link 2');
  });
});
