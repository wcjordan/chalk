import React from 'react';
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
const selectedLabels = ['5 minutes', 'work', 'home', 'low-energy', 'mobile'];

export default {
  title: 'Label Filter',
  component: LabelFilter,
};
export const DefaultLabelFilter: React.FC = () => (
  <LabelFilter labels={labels} selectedLabels={selectedLabels} />
);
