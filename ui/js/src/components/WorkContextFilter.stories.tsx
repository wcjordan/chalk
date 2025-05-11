import React from 'react';
import { Provider } from 'react-redux';
import { setupStore } from '../redux/store';
import WorkContextFilter from './WorkContextFilter';

const wrapper = (component) => (
  <Provider store={setupStore()}>{component}</Provider>
);

const defaultProps = {
  activeWorkContext: undefined,
};

export default {
  title: 'Work Context Filter',
  component: WorkContextFilter,
};
export const DefaultWorkContextFilter: React.FC = () =>
  wrapper(<WorkContextFilter {...defaultProps} />);

export const ActiveWorkContextFilter: React.FC = () =>
  wrapper(<WorkContextFilter {...defaultProps} activeWorkContext="urgent" />);
