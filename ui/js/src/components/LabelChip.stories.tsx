import React from 'react';
import { StyleSheet, View } from 'react-native';
import LabelChip from './LabelChip';

const styles = StyleSheet.create({
  wrapper: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
});
const wrapper = (chip) => <View style={styles.wrapper}>{chip}</View>;

const defaultProps = {
  label: 'errand',
  selected: false,
  onPress: () => null,
};

export default {
  title: 'Label Chip',
  component: LabelChip,
};
export const DefaultLabelChip: React.FC = () =>
  wrapper(<LabelChip {...defaultProps} />);

export const SelectedLabelChip: React.FC = () =>
  wrapper(<LabelChip {...defaultProps} selected={true} />);

export const ReadOnlyLabelChip: React.FC = () =>
  wrapper(<LabelChip {...defaultProps} onPress={undefined} />);
