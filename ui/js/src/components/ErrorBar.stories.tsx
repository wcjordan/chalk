import React from 'react';
import { StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import ErrorBar from './ErrorBar';

const styles = StyleSheet.create({
  wrapper: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    height: '100%',
    paddingTop: '60px',
    padddingBottom: '40px',
  },
});
const wrapper = (snackbar) => (
  <SafeAreaProvider>
    <View style={styles.wrapper}>{snackbar}</View>
  </SafeAreaProvider>
);

export default {
  title: 'Error Bar',
  component: ErrorBar,
};
export const DefaultErrorBar: React.FC = () =>
  wrapper(<ErrorBar dismissNotification={() => null} text="Snacks!" />);

export const HiddenErrorBar: React.FC = () => wrapper(<ErrorBar text={null} />);

export const PermanentErrorBar: React.FC = () =>
  wrapper(<ErrorBar text="Permanent snacks!" permanent={true} />);
