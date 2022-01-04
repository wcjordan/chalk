import Constants from 'expo-constants';
import { useEffect } from 'react';
import store from './redux/store';
import { listLabels, listTodos } from './redux/reducers';

export function useDataLoader() {
  if (Constants.manifest?.extra?.ENVIRONMENT === 'test') {
    return;
  }

  useEffect(() => {
    store.dispatch(listLabels());
    const intervalId = window.setInterval(
      () => store.dispatch(listTodos()),
      3000,
    );

    return () => {
      window.clearInterval(intervalId);
    };
  }, []);
}
