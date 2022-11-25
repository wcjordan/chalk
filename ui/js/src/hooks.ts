import { useEffect } from 'react';

import getStore from './redux/store';
import { listLabels, listTodos } from './redux/reducers';
import { getEnvFlags } from './helpers';

export function useDataLoader() {
  if (getEnvFlags().ENVIRONMENT === 'test') {
    return;
  }

  useEffect(() => {
    const store = getStore();
    store.dispatch(listLabels());

    const intervalId = window.setInterval(
      () => store.dispatch(listTodos()),
      10000,
    );

    return () => {
      window.clearInterval(intervalId);
    };
  }, []);
}
