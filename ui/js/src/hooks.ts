import Constants from 'expo-constants';
import { useEffect } from 'react';
import getStore from './redux/store';
import { listLabels, listTodos } from './redux/reducers';

export function useDataLoader() {
  if (Constants.manifest?.extra?.ENVIRONMENT === 'test') {
    return;
  }

  useEffect(() => {
    const store = getStore();
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
