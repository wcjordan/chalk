import { cleanup, renderHook } from '@testing-library/react-hooks';
import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import { useDataLoader } from './hooks';
import getStore from './redux/store';

const mockStore = configureMockStore([thunk])({
  labelsApi: {
    loading: false,
  },
  todosApi: {
    loading: false,
  },
});
const storeGetter = () => mockStore;
jest.mock('./redux/store', () => ({
  __esModule: true,
  default: storeGetter,
}));

jest.mock('expo-constants', () => ({
  manifest: {
    extra: {
      ENVIRONMENT: 'not_test',
    },
  },
}));

describe('useDataLoader', function () {
  it('should setup loading labels and todos', function () {
    jest.useFakeTimers();

    renderHook(useDataLoader);

    let actions = getStore().getActions();
    expect(actions.length).toEqual(1);
    expect(actions[0].type).toEqual('labelsApi/list/pending');

    // Move forward long enough to load Todos
    jest.advanceTimersByTime(10000);
    actions = getStore().getActions();
    expect(actions.length).toEqual(2);
    expect(actions[1].type).toEqual('todosApi/list/pending');

    // Move forward long enough to load Todos again
    jest.advanceTimersByTime(10000);
    actions = getStore().getActions();
    expect(actions.length).toEqual(3);
    expect(actions[2].type).toEqual('todosApi/list/pending');

    cleanup();

    // Ensure no more Todos are loaded after cleanup
    jest.advanceTimersByTime(30000);
    actions = getStore().getActions();
    expect(actions.length).toEqual(3);
  });
});

export {};
