import React, { useCallback } from 'react';
import {
  View,
  NativeSyntheticEvent,
  TextInputSubmitEditingEventData,
} from 'react-native';
import { Card, TextInput } from 'react-native-paper';

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
      <Card>
        <Card.Content>
          <TextInput
            testID="add-todo-input"
            placeholder="Add a new todo..."
            onSubmitEditing={addTodo}
          />
        </Card.Content>
      </Card>
    </View>
  );
};

type Props = {
  createTodo: (description: string) => void;
};

export default AddTodo;
