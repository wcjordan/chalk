import React, { useCallback } from 'react';
import { StyleSheet, Text, TextStyle, ViewStyle } from 'react-native';
import { IconButton } from 'react-native-paper';

interface Style {
  iconButton: ViewStyle;
  toggles: TextStyle;
}

const styles = StyleSheet.create<Style>({
  iconButton: {
    margin: 0,
  },
  toggles: {
    paddingRight: 8,
  },
});

const FilterViewControls: React.FC<Props> = function (props: Props) {
  const {
    isFiltered,
    showCompletedTodos,
    showLabelFilter,
    toggleShowCompletedTodos,
    toggleShowLabelFilter,
  } = props;

  let filterIcon = null;
  if (isFiltered) {
    filterIcon = (
      <IconButton
        iconColor="#000"
        icon={'filter'}
        key="filtered"
        size={20}
        style={styles.iconButton}
      />
    );
  }

  const toggleShowLabelFilterCb = useCallback(() => {
    toggleShowLabelFilter();
  }, [toggleShowLabelFilter]);
  const toggleShowCompletedTodosCb = useCallback(() => {
    toggleShowCompletedTodos();
  }, [toggleShowCompletedTodos]);

  return (
    <Text style={styles.toggles}>
      {filterIcon}
      <IconButton
        iconColor="#000"
        icon={showLabelFilter ? 'tag-multiple' : 'tag-multiple-outline'}
        key="show-labels"
        onPress={toggleShowLabelFilterCb}
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
        onPress={toggleShowCompletedTodosCb}
        selected={showCompletedTodos}
        size={20}
        style={styles.iconButton}
        testID="show-completed-todos"
      />
    </Text>
  );
};

type Props = {
  isFiltered: boolean;
  showCompletedTodos: boolean;
  showLabelFilter: boolean;
  toggleShowCompletedTodos: () => void;
  toggleShowLabelFilter: () => void;
};

export default FilterViewControls;
