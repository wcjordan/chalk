import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { FilterState } from '../redux/types';
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
  const { labels, selectedLabels, toggleLabel } = props;

  const filterByLabelCb = useCallback(
    (label: string) => {
      toggleLabel(label);
    },
    [toggleLabel],
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
  toggleLabel: (label: string) => void;
  labels: string[];
  selectedLabels: FilterState;
};

export default LabelFilter;
