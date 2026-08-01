import React from 'react';
import { StyleSheet, Text, TextStyle, View, ViewStyle } from 'react-native';

interface Style {
  container: ViewStyle;
  text: TextStyle;
}

const styles = StyleSheet.create<Style>({
  container: {
    backgroundColor: '#b71c1c',
    paddingVertical: 8,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  text: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
});

type Props = {
  visible: boolean;
};

const OfflineBanner: React.FC<Props> = function ({ visible }) {
  return (
    <View
      style={[styles.container, { display: visible ? 'flex' : 'none' }]}
      testID="offline-banner"
    >
      <Text style={styles.text}>You are offline</Text>
    </View>
  );
};

export default OfflineBanner;
