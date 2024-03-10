import React from 'react';
import { Provider } from 'react-redux';
import { FILTER_STATUS } from '../redux/types';
import { setupStore } from '../redux/store';
import LabelFilter from './LabelFilter';

const wrapper = (component) => (
  <Provider store={setupStore()}>
    {component}
  </Provider>
);

const labels = [
  'low-energy',
  'high-energy',
  'vague',
  'work',
  'home',
  'errand',
  'mobile',
  'desktop',
  'email',
  'urgent',
  '5 minutes',
  '25 minutes',
  '60 minutes',
];
const selectedLabels = {
  '5 minutes': FILTER_STATUS.Active,
  work: FILTER_STATUS.Inverted,
  home: FILTER_STATUS.Active,
  'low-energy': FILTER_STATUS.Active,
  mobile: FILTER_STATUS.Active,
};

export default {
  title: 'Label Filter',
  component: LabelFilter,
};
export const DefaultLabelFilter: React.FC = () => (wrapper(
  <LabelFilter labels={labels} selectedLabels={selectedLabels} />
));
