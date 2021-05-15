import React, { useCallback } from 'react';
import {
  View,
  NativeSyntheticEvent,
  StyleSheet,
  TextInputSubmitEditingEventData,
  TextStyle,
} from 'react-native';
import { TextInput } from 'react-native-paper';

interface Style {
  addTodoInput: TextStyle;
}

const styles = StyleSheet.create<Style>({
  addTodoInput: {
    borderTopLeftRadius: 0,
    borderTopRightRadius: 0,
    paddingBottom: 4,
    paddingTop: 4,
  },
});

const AddTodo: React.FC<Props> = function (props: Props) {
  const { createTodo } = props;
  const addTodo = useCallback(
    (event: NativeSyntheticEvent<TextInputSubmitEditingEventData>) => {
      if (event.key !== 'Enter' || event.shiftKey) {
        return;
      }
      createTodo(event.target.value);
    },
    [createTodo],
  );

  return (
    <View>
      <TextInput
        multiline={true}
        numberOfLines={3}
        onKeyPress={addTodo}
        placeholder="Add a new todo..."
        style={styles.addTodoInput}
        testID="add-todo-input"
      />
    </View>
  );
};

type Props = {
  createTodo: (description: string) => void;
};

export default AddTodo;
