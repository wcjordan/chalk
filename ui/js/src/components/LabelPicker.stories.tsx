import React from 'react';
import LabelPicker from './LabelPicker';

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
  '5 minutes': true,
  work: true,
  home: true,
  'low-energy': true,
  mobile: true,
};

export default {
  title: 'Label Picker',
  component: LabelPicker,
};
export const DefaultLabelPicker: React.FC = () => (
  <LabelPicker labels={labels} selectedLabels={selectedLabels} visible={true} />
);
