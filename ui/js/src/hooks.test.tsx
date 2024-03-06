import { cleanup, renderHook } from '@testing-library/react-hooks';
import { waitFor } from '@testing-library/react';
import fetchMock from 'fetch-mock-jest';
import { Provider } from 'react-redux'
import React, { PropsWithChildren } from 'react';

import { useDataLoader } from './hooks';
import { setupStore } from './redux/store';

// Pretend not a test so useDataLoader doesn't bail on requests
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
    const labelEntries = [{
      id: 1,
      name: "home"
    }, {
      id: 2,
      name: "work"
    }];
    fetchMock.getOnce('http://chalk-dev.flipperkid.com/api/todos/labels/', {
      body: labelEntries,
    });

    const firstTodo = {
      id: 256,
      description: "First Todo",
    };
    const secondTodo = Object.assign({}, firstTodo, {
      id: 257,
      description: "Second Todo"
    });
    const todosRoute = 'http://chalk-dev.flipperkid.com/api/todos/todos/';
    fetchMock.getOnce(todosRoute, {
      body: [firstTodo],
    });

    jest.useFakeTimers();

    const store = setupStore();
    const wrapper = ({ children }: PropsWithChildren<object>): JSX.Element => <Provider store={store}>{children}</Provider>;
    renderHook(useDataLoader, { wrapper });

    // Verify loading labels started
    expect(store.getState().labelsApi.loading).toEqual(true);

    // Verify loading labels completed
    await waitFor(() => {
      expect(store.getState().labelsApi.loading).toEqual(false);
      expect(store.getState().labelsApi.entries).toEqual(labelEntries);
    });

    // Move forward long enough to load Todos
    jest.advanceTimersByTime(10000);

    // Verify loading todos completed
    expect(store.getState().todosApi.loading).toEqual(true);
    await waitFor(() => {
      expect(store.getState().todosApi.loading).toEqual(false);
      expect(store.getState().todosApi.entries).toEqual([firstTodo]);
    });

    // Move forward long enough to load Todos again
    fetchMock.get(todosRoute, {
      body: [firstTodo, secondTodo],
    }, { overwriteRoutes: true });
    jest.advanceTimersByTime(10000);

    // Verify todos updated with a 2nd after loading again
    expect(store.getState().todosApi.loading).toEqual(true);
    await waitFor(() => {
      expect(store.getState().todosApi.loading).toEqual(false);
      expect(store.getState().todosApi.entries).toEqual([firstTodo, secondTodo]);
    });

    // Ensure no more Todos are loaded after cleanup
    cleanup();
    jest.advanceTimersByTime(30000);
    await fetchMock.flush();
    expect(fetchMock.calls().length).toEqual(3);

    // Verify we make the server requests
    expect(fetchMock).toBeDone();
  }, 20000);
});

export {};
