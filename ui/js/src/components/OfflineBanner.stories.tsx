import React from 'react';
import { StyleSheet, View } from 'react-native';
import { Provider } from 'react-redux';
import { setupStore } from '../redux/store';
import OfflineBanner from './OfflineBanner';

const styles = StyleSheet.create({
  wrapper: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    height: '100%',
  },
});

const wrapper = (component) => (
  <Provider store={setupStore()}>
    <View style={styles.wrapper}>{component}</View>
  </Provider>
);

export default {
  title: 'Offline Banner',
  component: OfflineBanner,
};

export const VisibleOfflineBanner: React.FC = () =>
  wrapper(<OfflineBanner visible={true} />);

export const HiddenOfflineBanner: React.FC = () =>
  wrapper(<OfflineBanner visible={false} />);
