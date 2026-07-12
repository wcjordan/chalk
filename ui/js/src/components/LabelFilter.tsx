import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { useAppSelector, useAppDispatch } from '../hooks/hooks';
import { selectLabelNames } from '../selectors';
import { toggleLabel } from '../redux/reducers';
import FilterViewControls from './FilterViewControls';
import LabelChip from './LabelChip';

interface Style {
  labelFilterView: ViewStyle;
  spacer: ViewStyle;
}

const UNLABELED = 'Unlabeled';
const SNOOZED = 'snoozed';
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

const LabelFilter: React.FC = function () {
  const dispatch = useAppDispatch();
  const labels = useAppSelector(selectLabelNames);
  const {
    filterLabels: selectedLabels,
    showCompletedTodos,
    showLabelFilter,
  } = useAppSelector((state) => state.workspace);

  const filterByLabelCb = useCallback((label: string) => {
    dispatch(toggleLabel(label));
  }, []);

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
      <LabelChip
        display="Snoozed"
        key={SNOOZED}
        label={SNOOZED}
        onPress={filterByLabelCb}
        status={selectedLabels[SNOOZED]}
      />
      <View style={styles.spacer} />
      <FilterViewControls
        isFiltered={Object.keys(selectedLabels).length > 0}
        showCompletedTodos={showCompletedTodos}
        showLabelFilter={showLabelFilter}
      />
    </View>
  );
};

export default LabelFilter;
