import React, { useCallback, useState } from 'react';
import { StyleSheet, TextStyle, View, ViewStyle } from 'react-native';
import { TextInput } from 'react-native-paper';

interface Style {
  addTodoView: ViewStyle;
  addTodoInput: TextStyle;
}

const styles = StyleSheet.create<Style>({
  addTodoView: {
    width: '100%',
    maxHeight: 104,
  },
  addTodoInput: {
    borderTopLeftRadius: 0,
    borderTopRightRadius: 0,
    paddingBottom: 4,
    paddingTop: 4,
  },
});

const AddTodo: React.FC<Props> = function (props: Props) {
  const { createTodo } = props;
  const [textValue, setTextValue] = useState('');

  const addTodo = useCallback(() => {
    createTodo(textValue);
    setTextValue('');
  }, [createTodo, textValue]);

  return (
    <View style={styles.addTodoView}>
      <TextInput
        blurOnSubmit={true}
        multiline={true}
        numberOfLines={3}
        onChangeText={setTextValue}
        onSubmitEditing={addTodo}
        placeholder="Add a new todo..."
        style={styles.addTodoInput}
        testID="add-todo-input"
        value={textValue}
      />
    </View>
  );
};

type Props = {
  createTodo: (description: string) => void;
};

export default AddTodo;
