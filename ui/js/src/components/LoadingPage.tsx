import React from 'react';
import { StyleSheet, ViewStyle } from 'react-native';
import { ActivityIndicator } from 'react-native-paper';

interface Style {
  loadingIndicator: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  loadingIndicator: {
    flex: 1,
    margin: 'auto',
  },
});

const LoadingPage: React.FC = function () {
  return (
    <React.Fragment>
      <ActivityIndicator size={'large'} style={styles.loadingIndicator} />
    </React.Fragment>
  );
};

export default LoadingPage;
