import React from 'react';
import { StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider } from 'react-redux';
import { setupStore } from '../redux/store';
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
const wrapper = (component) => (
  <SafeAreaProvider>
    <Provider store={setupStore()}>
      <View style={styles.wrapper}>{component}</View>
    </Provider>
  </SafeAreaProvider>
);

export default {
  title: 'Error Bar',
  component: ErrorBar,
};
export const DefaultErrorBar: React.FC = () => wrapper(<ErrorBar text="Snacks!" />);

export const HiddenErrorBar: React.FC = () => wrapper(<ErrorBar text={null} />);

export const PermanentErrorBar: React.FC = () =>
  wrapper(<ErrorBar text="Permanent snacks!" permanent={true} />);
