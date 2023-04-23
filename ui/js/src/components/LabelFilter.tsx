import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { FILTER_STATUS, FilterState } from '../redux/types';
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
  // TODO (jordan) memoize the conversion
  const { filterByLabels, labels, selectedLabels } = props;

  const filterByLabelCb = useCallback(
    (label: string) => {
      const newLabels = Object.assign({}, selectedLabels);
      const prevStatus = newLabels[label];
      if (prevStatus === FILTER_STATUS.Active) {
        // Invert existing item
        newLabels[label] = FILTER_STATUS.Inverted;
      } else if (prevStatus === FILTER_STATUS.Inverted) {
        // Delete inverted item
        delete newLabels[label];
      } else {
        newLabels[label] = FILTER_STATUS.Active;
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
      status={selectedLabels[label]}
    />
  ));
  return (
    <View style={styles.labelFilterView} testID="label-filter">
      {chips}
      <LabelChip
        key={UNLABELED}
        label={UNLABELED}
        onPress={filterByLabelCb}
        status={selectedLabels[UNLABELED]}
      />
    </View>
  );
};

type Props = {
  filterByLabels: (labels: FilterState) => void;
  labels: string[];
  selectedLabels: FilterState;
};

export default LabelFilter;
