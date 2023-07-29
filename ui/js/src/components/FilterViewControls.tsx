import React from 'react';
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
    showCompletedTodos,
    showLabelFilter,
    toggleShowCompletedTodos,
    toggleShowLabelFilter,
  } = props;

  return (
    <Text style={styles.toggles}>
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
    </Text>
  );
};

type Props = {
  showCompletedTodos: boolean;
  showLabelFilter: boolean;
  toggleShowCompletedTodos: () => void;
  toggleShowLabelFilter: () => void;
};

export default FilterViewControls;
