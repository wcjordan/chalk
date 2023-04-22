import React from 'react';
import { StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
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

const styles = StyleSheet.create({
  wrapper: {
    paddingTop: '100px',
    padddingBottom: '100px',
  },
});
const wrapper = (labelPicker) => (
  <SafeAreaProvider>
    <View style={styles.wrapper}>{labelPicker}</View>
  </SafeAreaProvider>
);

export default {
  title: 'Label Picker',
  component: LabelPicker,
};
export const DefaultLabelPicker: React.FC = () =>
  wrapper(
    <LabelPicker
      labels={labels}
      selectedLabels={selectedLabels}
      visible={true}
    />,
  );
