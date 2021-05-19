import _ from 'lodash';
import { connect, ConnectedProps } from 'react-redux';
import React from 'react';
import {
  Platform,
  ScrollView,
  StatusBar,
  StyleProp,
  StyleSheet,
  View,
  ViewStyle,
} from 'react-native';
import AddTodo from './components/AddTodo';
import { ReduxState } from './redux/types';
import TodoItem from './components/TodoItem';
import { createTodo, updateTodo, setTodoEditId } from './redux/reducers';

interface Style {
  root: ViewStyle;
  containerMobile: ViewStyle;
  containerWeb: ViewStyle;
}
interface TopStyle {
  top: ViewStyle;
}

const styles = StyleSheet.create<Style>({
  root: {
    height: '100%',
    width: '100%',
    backgroundColor: '#364263',
  },
  containerMobile: {
    height: '100%',
    width: '100%',
  },
  containerWeb: {
    height: '100%',
    width: '66%',
    marginHorizontal: 'auto',
  },
});

export const App: React.FC<ConnectedProps<typeof connector>> = function (
  props: ConnectedProps<typeof connector>,
) {
  const { createTodo, setTodoEditId, todos, updateTodo, workspace } = props;
  const { editId } = workspace;
  const todoViews = _.map(todos, (todo) => (
    <TodoItem
      editing={todo.id === editId}
      key={todo.id || ''}
      setTodoEditId={setTodoEditId}
      todo={todo}
      updateTodo={updateTodo}
    />
  ));

  let containerStyle: StyleProp<ViewStyle> =
    Platform.OS === 'web' ? styles.containerWeb : styles.containerMobile;
  const paddingTop = Platform.OS === 'android' ? StatusBar.currentHeight : 80;
  const topStyle = StyleSheet.create<TopStyle>({
    top: {
      paddingTop: paddingTop,
    },
  });
  containerStyle = StyleSheet.compose(containerStyle, topStyle.top);
  return (
    <View style={styles.root}>
      <View testID="todo-list" style={containerStyle}>
        <AddTodo createTodo={createTodo} />
        <ScrollView>{todoViews}</ScrollView>
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
