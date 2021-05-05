import _ from 'lodash';
import { connect, ConnectedProps } from 'react-redux';
import React from 'react';
import { Platform, StatusBar, StyleSheet, View, ViewStyle } from 'react-native';
import { Appbar } from 'react-native-paper';
import AddTodo from './components/AddTodo';
import { ReduxState } from './redux/types';
import TodoItem from './components/TodoItem';
import { createTodo, updateTodo, setTodoEditId } from './redux/reducers';

/* Color palette
https://coolors.co/3d5a80-98c1d9-e0fbfc-ee6c4d-293241
#e0fbfc - light
#98c1d9 - medium
#3d5a80 - dark
#293241 - near black
#ee6c4d - stand out
*/

interface Style {
  root: ViewStyle;
  container: ViewStyle;
}
interface TopStyle {
  top: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  root: {
    height: '100%',
    width: '100%',
    backgroundColor: '#293241',
  },
  container: {
    height: '100%',
    width: '66%',
    marginHorizontal: 'auto',
  },
});

const bottomStyles = StyleSheet.create({
  bottom: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
  },
});

export const App: React.FC<ConnectedProps<typeof connector>> = function (
  props: ConnectedProps<typeof connector>,
) {
  const { createTodo, setTodoEditId, todos, updateTodo, workspace } = props;
  const { editId, uncommittedEdits } = workspace;
  const todoViews = _.map(todos, (todo) => (
    <TodoItem
      editing={todo.id === editId}
      key={todo.id || ''}
      setTodoEditId={setTodoEditId}
      todo={todo}
      uncommittedEdit={uncommittedEdits[todo.id]}
      updateTodo={updateTodo}
    />
  ));

  const paddingTop = Platform.OS === 'android' ? StatusBar.currentHeight : 80;
  const topStyle = StyleSheet.create<TopStyle>({
    top: {
      paddingTop: paddingTop,
    },
  }).top;
  const containerStyles = StyleSheet.compose(styles.container, topStyle);
  return (
    <View style={styles.root}>
      <Appbar style={bottomStyles.bottom}>
        <Appbar.Action
          icon="archive"
          onPress={() => console.log('Pressed archive')}
        />
        <Appbar.Action
          icon="mail"
          onPress={() => console.log('Pressed mail')}
        />
        <Appbar.Action
          icon="label"
          onPress={() => console.log('Pressed label')}
        />
        <Appbar.Action
          icon="delete"
          onPress={() => console.log('Pressed delete')}
        />
      </Appbar>
      <View nativeID="todo-list" style={containerStyles}>
        <AddTodo createTodo={createTodo} />
        {todoViews}
      </View>
    </View>
  );
};

const mapStateToProps = (state: ReduxState) => {
  return {
    todos: state.todosApi.entries,
    workspace: state.workspace,
  };
};
const mapDispatchToProps = { createTodo, setTodoEditId, updateTodo };
const connector = connect(mapStateToProps, mapDispatchToProps);
export default connector(App);
