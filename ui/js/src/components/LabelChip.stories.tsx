import React from 'react';
import { StyleSheet, View } from 'react-native';
import { FILTER_STATUS } from '../redux/types';
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

export const ActiveLabelChip: React.FC = () =>
  wrapper(<LabelChip {...defaultProps} status={FILTER_STATUS.Active} />);

export const InvertedLabelChip: React.FC = () =>
  wrapper(<LabelChip {...defaultProps} status={FILTER_STATUS.Inverted} />);

export const ReadOnlyLabelChip: React.FC = () =>
  wrapper(<LabelChip {...defaultProps} onPress={undefined} />);

export const DisplayNameLabelChip: React.FC = () =>
  wrapper(<LabelChip {...defaultProps} display="Display name" />);
