import React from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { ActivityIndicator } from 'react-native-paper';

interface Style {
  loadingIndicator: ViewStyle;
  spacer: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  loadingIndicator: {
    margin: 'auto',
  },
  spacer: {
    flexGrow: 1,
    minHeight: 20,
  },
});

const LoadingPage: React.FC = function () {
  return (
    <React.Fragment>
      <View style={styles.spacer} key="spacer-before" />
      <ActivityIndicator size={'large'} style={styles.loadingIndicator} />
      <View style={styles.spacer} key="spacer-after" />
    </React.Fragment>
  );
};

export default LoadingPage;
