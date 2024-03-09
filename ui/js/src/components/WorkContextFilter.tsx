import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { FILTER_STATUS } from '../redux/types';
import { setWorkContext } from '../redux/reducers';
import { useAppDispatch } from '../hooks';
import { workContexts } from '../redux/workspaceSlice';
import LabelChip from './LabelChip';
import FilterViewControls from './FilterViewControls';

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
  const dispatch = useAppDispatch();
  const {
    activeWorkContext,
    isFiltered,
    showCompletedTodos,
  } = props;

  const setWorkContextCb = useCallback(
    (workContext: string) => {
      dispatch(setWorkContext(workContext));
    },
    [],
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
        isFiltered={isFiltered}
        showCompletedTodos={showCompletedTodos}
        showLabelFilter={false}
      />
    </View>
  );
};

type Props = {
  activeWorkContext: string | undefined;
  isFiltered: boolean;
  showCompletedTodos: boolean;
};

export default WorkContextFilter;
