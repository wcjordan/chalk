import React, { useCallback } from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { IconButton } from 'react-native-paper';
import { FILTER_STATUS, WorkContext } from '../redux/types';
import LabelChip from './LabelChip';

interface Style {
  filterView: ViewStyle;
  iconButton: ViewStyle;
  spacer: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  filterView: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    width: '100%',
    backgroundColor: '#d9f0ffff',
  },
  iconButton: {
    margin: 0,
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
      <IconButton
        iconColor="#000"
        icon={showLabelFilter ? 'tag-multiple' : 'tag-multiple-outline'}
        key="show-labels"
        onPress={toggleShowLabelFilter}
        selected={showLabelFilter}
        size={20}
        style={styles.iconButton}
        testID="show-labels"
      />
      <IconButton
        iconColor="#000"
        icon={
          showCompletedTodos
            ? 'checkbox-marked-outline'
            : 'checkbox-blank-outline'
        }
        key="show-completed"
        onPress={toggleShowCompletedTodos}
        selected={showCompletedTodos}
        size={20}
        style={styles.iconButton}
        testID="show-completed-todos"
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
