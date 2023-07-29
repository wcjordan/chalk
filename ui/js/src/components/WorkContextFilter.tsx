import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { FILTER_STATUS, WorkContext } from '../redux/types';
import FilterViewControls from './FilterViewControls';
import LabelChip from './LabelChip';

interface Style {
  filterView: ViewStyle;
  spacer: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  filterView: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    width: '100%',
    backgroundColor: '#d9f0ffff',
  },
  spacer: {
    flexGrow: 1,
  },
});

const WorkContextFilter: React.FC<Props> = function (props: Props) {
  const {
    activeWorkContext,
    setWorkContext,
    showCompletedTodos,
    showLabelFilter,
    toggleShowCompletedTodos,
    toggleShowLabelFilter,
    workContexts,
  } = props;

  const setWorkContextCb = useCallback(
    (workContext: string) => {
      setWorkContext(workContext);
    },
    [setWorkContext],
  );

  const chips = Object.keys(workContexts).map((workContext) => (
    <LabelChip
      display={workContexts[workContext].displayName}
      key={workContext}
      label={workContext}
      onPress={setWorkContextCb}
      status={
        workContext === activeWorkContext ? FILTER_STATUS.Active : undefined
      }
    />
  ));
  return (
    <View style={styles.filterView} testID="work-context-filter">
      {chips}
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
  activeWorkContext: string | undefined;
  setWorkContext: (workContext: string) => void;
  showCompletedTodos: boolean;
  showLabelFilter: boolean;
  toggleShowCompletedTodos: () => void;
  toggleShowLabelFilter: () => void;
  workContexts: { [key: string]: WorkContext };
};

export default WorkContextFilter;
