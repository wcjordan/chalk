import React from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { ActivityIndicator } from 'react-native-paper';

interface Style {
  wrapper: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  wrapper: {},
});

const LoadingPage: React.FC = function () {
  return (
    <View style={styles.wrapper}>
      <ActivityIndicator size={'large'} />
    </View>
  );
};

export default LoadingPage;
