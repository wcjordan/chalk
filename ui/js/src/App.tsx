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
import LabelPicker from './components/LabelPicker';
import { ReduxState } from './redux/types';
import TodoItem from './components/TodoItem';
import {
  createTodo,
  updateTodo,
  setTodoEditId,
  setTodoLabelingId,
} from './redux/reducers';

interface Style {
  root: ViewStyle;
  containerMobile: ViewStyle;
  containerWeb: ViewStyle;
}
interface TopStyle {
  top: ViewStyle;
}

// --columbia-blue: #d9f0ffff;
// --baby-blue-eyes: #a3d5ffff;
// --light-sky-blue: #83c9f4ff;
// --oxford-blue: #061a40ff;
// --usafa-blue: #0353a4ff;

const BG_COLOR = '#061a40ff';
const styles = StyleSheet.create<Style>({
  root: {
    height: '100%',
    width: '100%',
    backgroundColor: BG_COLOR,
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
  const {
    createTodo,
    setTodoEditId,
    setTodoLabelingId,
    todos,
    updateTodo,
    workspace,
  } = props;
  const { editId, labelTodoId, labels, selectedLabels } = workspace;
  const todoViews = _.map(todos, (todo) => (
    <TodoItem
      setTodoLabelingId={setTodoLabelingId}
      editing={todo.id === editId}
      key={todo.id || ''}
      setTodoEditId={setTodoEditId}
      todo={todo}
      updateTodo={updateTodo}
    />
  ));

  let containerStyle: StyleProp<ViewStyle> =
    Platform.OS === 'web' ? styles.containerWeb : styles.containerMobile;
  if (Platform.OS === 'web') {
    const topStyle = StyleSheet.create<TopStyle>({
      top: {
        paddingTop: 80,
      },
    }).top;
    containerStyle = StyleSheet.compose(containerStyle, topStyle);
  }

  return (
    <View style={styles.root}>
      <StatusBar
        animated={true}
        backgroundColor={BG_COLOR}
        barStyle={'light-content'}
      />
      <View style={containerStyle}>
        <AddTodo createTodo={createTodo} />
        <ScrollView testID="todo-list">{todoViews}</ScrollView>
      </View>
      <LabelPicker
        labels={labels}
        selectedLabels={selectedLabels}
        setTodoLabelingId={setTodoLabelingId}
        visible={labelTodoId !== null}
      />
    </View>
  );
};

const mapStateToProps = (state: ReduxState) => {
  return {
    todos: state.todosApi.entries,
    workspace: state.workspace,
  };
};
const mapDispatchToProps = {
  createTodo,
  setTodoEditId,
  setTodoLabelingId,
  updateTodo,
};
const connector = connect(mapStateToProps, mapDispatchToProps);
export default connector(App);
