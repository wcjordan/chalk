import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { FilterState } from '../redux/types';
import FilterViewControls from './FilterViewControls';
import LabelChip from './LabelChip';

interface Style {
  labelFilterView: ViewStyle;
  spacer: ViewStyle;
}

const UNLABELED = 'Unlabeled';
const styles = StyleSheet.create<Style>({
  labelFilterView: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    width: '100%',
    backgroundColor: '#d9f0ffff',
  },
  spacer: {
    flexGrow: 1,
  },
});

const LabelFilter: React.FC<Props> = function (props: Props) {
  // TODO (jordan) memoize the conversion
  const {
    labels,
    selectedLabels,
    showCompletedTodos,
    showLabelFilter,
    toggleLabel,
    toggleShowCompletedTodos,
    toggleShowLabelFilter,
  } = props;

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
      <View style={styles.spacer} />
      <FilterViewControls
        showCompletedTodos={showCompletedTodos}
        showLabelFilter={showLabelFilter}
        toggleShowCompletedTodos={toggleShowCompletedTodos}
        toggleShowLabelFilter={toggleShowLabelFilter}
      />
    </View>
  );
};

type Props = {
  labels: string[];
  selectedLabels: FilterState;
  showCompletedTodos: boolean;
  showLabelFilter: boolean;
  toggleLabel: (label: string) => void;
  toggleShowCompletedTodos: () => void;
  toggleShowLabelFilter: () => void;
};

export default LabelFilter;
