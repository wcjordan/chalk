import React from 'react';
import { Provider } from 'react-redux';
import { FILTER_STATUS } from '../redux/types';
import { setupStore } from '../redux/store';
import LabelFilter from './LabelFilter';

const defaultState = {
  labelsApi: {
    entries: [
      { name: 'low-energy' },
      { name: 'high-energy' },
      { name: 'vague' },
      { name: 'work' },
      { name: 'home' },
      { name: 'errand' },
      { name: 'mobile' },
      { name: 'desktop' },
      { name: 'email' },
      { name: 'urgent' },
      { name: '5 minutes' },
      { name: '25 minutes' },
      { name: '60 minutes' },
    ],
  },
  workspace: {
    filterLabels: {
      '5 minutes': FILTER_STATUS.Active,
      work: FILTER_STATUS.Inverted,
      home: FILTER_STATUS.Active,
      'low-energy': FILTER_STATUS.Active,
      mobile: FILTER_STATUS.Active,
    },
  },
};

const wrapper = (component) => (
  <Provider store={setupStore(defaultState)}>{component}</Provider>
);

export default {
  title: 'Label Filter',
  component: LabelFilter,
};
export const DefaultLabelFilter: React.FC = () => wrapper(<LabelFilter />);
