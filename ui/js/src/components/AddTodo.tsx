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
  },
});

const AddTodo: React.FC<Props> = function (props: Props) {
  const { createTodo } = props;
  const addTodo = useCallback(
    (event: NativeSyntheticEvent<TextInputSubmitEditingEventData>) => {
      createTodo(event.nativeEvent.text);
    },
    [createTodo],
  );

  return (
    <View>
      <TextInput
        style={styles.addTodoInput}
        testID="add-todo-input"
        placeholder="Add a new todo..."
        onSubmitEditing={addTodo}
      />
    </View>
  );
};

type Props = {
  createTodo: (description: string) => void;
};

export default AddTodo;
