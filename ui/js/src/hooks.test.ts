import { cleanup, renderHook } from '@testing-library/react-hooks';
import { waitFor } from '@testing-library/react';
import configureMockStore from 'redux-mock-store';
import fetchMock from 'fetch-mock-jest';
import thunk from 'redux-thunk';

import { useDataLoader } from './hooks';
import getStore from './redux/store';

const mockStore = configureMockStore([thunk])({
  labelsApi: {
    loading: false,
  },
  shortcuts: {
    latestGeneration: 1,
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
  expoConfig: {
    extra: {
      ENVIRONMENT: 'not_test',
    },
  },
}));

describe('useDataLoader', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should setup loading labels and todos', async function () {
    fetchMock.getOnce('http://chalk-dev.flipperkid.com/api/todos/labels/', {
      body: [],
    });
    fetchMock.get('http://chalk-dev.flipperkid.com/api/todos/todos/', {
      body: [],
    });

    jest.useFakeTimers();

    renderHook(useDataLoader);

    let actions = getStore().getActions();
    expect(actions.length).toEqual(1);
    expect(actions[0].type).toEqual('labelsApi/list/pending');
    await waitFor(() => {
      const actionTypes = getStore()
        .getActions()
        .map((action) => action.type);
      expect(actionTypes).toContainEqual('labelsApi/list/fulfilled');
    });
    expect(actions.length).toEqual(2);

    // Move forward long enough to load Todos
    jest.advanceTimersByTime(10000);
    actions = getStore().getActions();
    expect(actions.length).toEqual(4);
    expect(actions[2].type).toEqual('shortcuts/incrementGenerations');
    expect(actions[3].type).toEqual('todosApi/list/pending');
    await waitFor(() => {
      const actionTypes = getStore()
        .getActions()
        .map((action) => action.type);
      expect(actionTypes).toContainEqual('todosApi/list/fulfilled');
      expect(actionTypes).toContainEqual(
        'shortcuts/clearOperationsUpThroughGeneration',
      );
    });
    expect(actions.length).toEqual(6);

    // Move forward long enough to load Todos again
    jest.advanceTimersByTime(10000);
    actions = getStore().getActions();
    expect(actions.length).toEqual(8);
    expect(actions[6].type).toEqual('shortcuts/incrementGenerations');
    expect(actions[7].type).toEqual('todosApi/list/pending');

    cleanup();

    // Ensure no more Todos are loaded after cleanup
    jest.advanceTimersByTime(30000);
    actions = getStore().getActions();
    expect(actions.length).toEqual(8);

    // Verify we make the server requests
    expect(fetchMock).toBeDone();
  });
});

export {};
