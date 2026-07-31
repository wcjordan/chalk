import React, { useEffect } from 'react';
import { StatusBar, StyleSheet, ViewStyle } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import ErrorBar from './components/ErrorBar';
import Login from './components/Login';
import OfflineBanner from './components/OfflineBanner';
import TodoList from './components/TodoList';
import { useAppDispatch, useAppSelector } from './hooks/hooks';
import { useNetworkMonitor } from './hooks/useNetworkMonitor';
import { useOfflineQueueSync } from './hooks/useOfflineQueueSync';
import { flushOfflineQueue } from './redux/reducers';

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
  useNetworkMonitor();
  useOfflineQueueSync();
  const dispatch = useAppDispatch();
  const loggedIn = useAppSelector((state) => state.workspace.loggedIn);
  const isOnline = useAppSelector((state) => state.network.isOnline);

  useEffect(() => {
    if (isOnline) {
      dispatch(flushOfflineQueue());
    }
  }, [isOnline, dispatch]);

  const notificationQueue = useAppSelector(
    (state) => state.notifications.notificationQueue,
  );

  const content = !loggedIn ? <Login /> : <TodoList />;

  const currentNotification =
    notificationQueue.length > 0 ? notificationQueue[0] : null;
  const notificationText = currentNotification?.text ?? null;
  const notificationType = currentNotification?.type ?? undefined;
  return (
    <SafeAreaView style={styles.root}>
      <StatusBar
        animated={true}
        backgroundColor={BG_COLOR}
        barStyle={'light-content'}
      />
      <OfflineBanner visible={!isOnline} />
      {content}
      <ErrorBar
        key={notificationText}
        text={notificationText}
        notificationType={notificationType}
      />
    </SafeAreaView>
  );
};

export default App;
