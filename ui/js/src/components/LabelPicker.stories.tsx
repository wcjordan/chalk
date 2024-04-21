import React from 'react';
import { StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider } from 'react-redux';
import { setupStore } from '../redux/store';
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
const wrapper = (component) => (
  <SafeAreaProvider>
    <Provider store={setupStore()}>
      <View style={styles.wrapper}>{component}</View>
    </Provider>
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
