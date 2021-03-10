import React, { useCallback } from 'react';
import {
  StyleSheet,
  TextInput,
  View,
  NativeSyntheticEvent,
  TextInputSubmitEditingEventData,
} from 'react-native';

const styles = StyleSheet.create({
  addTodo: {
    backgroundColor: '#98c1d9',
    borderWidth: 0,
    display: 'flex',
    fontFamily: 'monospace',
    padding: 8,
    width: '100%',
  },
  addTodoInput: {
    backgroundColor: 'transparent',
    color: '#293241',
    fontFamily: 'inherit',
    fontSize: 20,
    marginLeft: 4,
    padding: 4,
    flexGrow: 1,
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

  // TODO remove input outline on focus
  return (
    <View style={styles.addTodo}>
      <TextInput
        nativeID="add-todo-input"
        style={styles.addTodoInput}
        placeholder="Add a new todo..."
        placeholderTextColor="#e0fbfc"
        onSubmitEditing={addTodo}
      />
    </View>
  );
};

type Props = {
  createTodo: (description: string) => void;
};

export default AddTodo;
