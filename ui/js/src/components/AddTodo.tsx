import React, { useCallback, useState } from 'react';
import { StyleSheet, TextStyle, View, ViewStyle } from 'react-native';
import { TextInput } from 'react-native-paper';
import { createTodo } from '../redux/reducers';
import { useAppDispatch } from '../hooks/hooks';

interface Style {
  addTodoView: ViewStyle;
  addTodoInput: ViewStyle;
  addTodoInputContent: TextStyle;
}

const styles = StyleSheet.create<Style>({
  addTodoView: {
    width: '100%',
    maxHeight: 104,
  },
  addTodoInput: {
    borderTopLeftRadius: 4,
    borderTopRightRadius: 4,
  },
  addTodoInputContent: {
    fontFamily: 'sans-serif',
    paddingBottom: 8,
    paddingLeft: 8,
    paddingRight: 8,
    paddingTop: 8,
  },
});

const AddTodo: React.FC = function () {
  const dispatch = useAppDispatch();
  const [textValue, setTextValue] = useState('');

  const addTodo = useCallback(() => {
    dispatch(createTodo(textValue));
    setTextValue('');
  }, [textValue]);

  return (
    <View style={styles.addTodoView}>
      <TextInput
        blurOnSubmit={true}
        contentStyle={styles.addTodoInputContent}
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

export default AddTodo;
