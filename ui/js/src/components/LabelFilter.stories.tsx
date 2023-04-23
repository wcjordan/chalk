import React from 'react';
import { FILTER_STATUS } from '../redux/types';
import LabelFilter from './LabelFilter';

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
export const DefaultLabelFilter: React.FC = () => (
  <LabelFilter labels={labels} selectedLabels={selectedLabels} />
);
