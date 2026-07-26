import React from 'react';
import { StyleSheet, View } from 'react-native';
import { Provider } from 'react-redux';
import { setupStore } from '../redux/store';
import SnoozeMenu from './SnoozeMenu';

const styles = StyleSheet.create({
  wrapper: {
    paddingTop: '100px',
    paddingBottom: '100px',
  },
});
const wrapper = (component) => (
  <Provider store={setupStore()}>
    <View style={styles.wrapper}>{component}</View>
  </Provider>
);

export default {
  title: 'Snooze Menu',
  component: SnoozeMenu,
};

export const DefaultSnoozeMenu: React.FC = () =>
  wrapper(<SnoozeMenu snoozeTodoId={1} visible={true} />);

export const HiddenSnoozeMenu: React.FC = () =>
  wrapper(<SnoozeMenu snoozeTodoId={null} visible={false} />);
