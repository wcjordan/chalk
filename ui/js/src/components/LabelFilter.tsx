import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import LabelChip from './LabelChip';

interface Style {
  labelFilterView: ViewStyle;
}

const UNLABELED = 'Unlabeled';
const styles = StyleSheet.create<Style>({
  labelFilterView: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    width: '100%',
    backgroundColor: '#d9f0ffff',
  },
});

const LabelFilter: React.FC<Props> = function (props: Props) {
  // TODO (jordan) Convert selectedLabels to a map for quick lookups
  // Also memoize the conversion
  const { filterByLabels, labels, selectedLabels } = props;

  const filterByLabelCb = useCallback(
    (label: string) => {
      const newLabels = Array.from(selectedLabels);
      const labelIndex = newLabels.indexOf(label);
      if (labelIndex > -1) {
        // Remove existing item
        newLabels.splice(labelIndex, 1);
      } else {
        newLabels.push(label);
      }

      filterByLabels(newLabels);
    },
    [filterByLabels, selectedLabels],
  );

  const chips = labels.map((label) => (
    <LabelChip
      key={label}
      label={label}
      onPress={filterByLabelCb}
      selected={selectedLabels.includes(label) || false}
    />
  ));
  return (
    <View style={styles.labelFilterView} testID="label-filter">
      {chips}
      <LabelChip
        key={UNLABELED}
        label={UNLABELED}
        onPress={filterByLabelCb}
        selected={selectedLabels.includes(UNLABELED) || false}
      />
    </View>
  );
};

type Props = {
  filterByLabels: (labels: string[]) => void;
  labels: string[];
  selectedLabels: string[];
};

export default LabelFilter;
