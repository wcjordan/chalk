import React from 'react';
import { SafeAreaView, StatusBar, StyleSheet, ViewStyle } from 'react-native';
import ErrorBar from './components/ErrorBar';
import Login from './components/Login';
import TodoList from './components/TodoList';
import { useAppSelector } from './hooks/hooks';

interface Style {
  root: ViewStyle;
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
});

const App: React.FC = function () {
  const loggedIn = useAppSelector((state) => state.workspace.loggedIn);
  const notificationQueue = useAppSelector(
    (state) => state.notifications.notificationQueue,
  );

  let content: React.JSX.Element | null = null;
  if (!loggedIn) {
    content = <Login />;
  } else {
    content = <TodoList />;
  }

  const notificationText =
    notificationQueue.length > 0 ? notificationQueue[0] : null;
  return (
    <SafeAreaView style={styles.root}>
      <StatusBar
        animated={true}
        backgroundColor={BG_COLOR}
        barStyle={'light-content'}
      />
      {content}
      <ErrorBar key={notificationText} text={notificationText} />
    </SafeAreaView>
  );
};

export default App;
