import '../__mocks__/matchMediaMock';
import fetchMock from 'fetch-mock-jest';
import labelsApiSlice, { getLabelsApi, listLabels } from './labelsApiSlice';
import { setupStore } from './store';

describe('listLabels', function () {
  afterEach(function () {
    fetchMock.restore();
  });

  it('should make a GET request and dispatch actions', async function () {
    const stubLabels = [
      getStubLabel({ id: 1, name: 'label 1' }),
      getStubLabel({ id: 2, name: 'label 2' }),
    ];
    fetchMock.getOnce(getLabelsApi(), {
      body: stubLabels,
    });

    const store = setupStore();
    await store.dispatch(listLabels());

    // Verify labels are loaded
    expect(store.getState().labelsApi.loading).toEqual(false);
    expect(store.getState().labelsApi.entries).toEqual(stubLabels);

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });

  it('should do nothing if labels are already loading', async function () {
    fetchMock.mock('*', 200);

    const store = setupStore({ labelsApi: { loading: true } });
    await store.dispatch(listLabels());

    // Verify we make the server request
    expect(fetchMock).not.toHaveFetched('*');
  });
});

describe('labelsApiSlice reducer', function () {
  const initialState = {
    entries: [],
    initialLoad: true,
    loading: false,
  };

  it('should return the initial state', function () {
    expect(labelsApiSlice.reducer(undefined, {})).toEqual(initialState);
  });

  describe('labelsApi/list/pending', function () {
    it('should mark loading as in progress', function () {
      const result = labelsApiSlice.reducer(initialState, {
        type: 'labelsApi/list/pending',
      });
      expect(result).toEqual({
        entries: [],
        initialLoad: true,
        loading: true,
      });
    });
  });

  describe('labelsApi/list/rejected', function () {
    let spy;

    beforeEach(function () {
      spy = jest.spyOn(console, 'warn').mockImplementation();
    });

    afterEach(function () {
      spy.mockRestore();
    });

    it('should mark loading as no longer in progress', function () {
      const result = labelsApiSlice.reducer(
        {
          entries: [],
          initialLoad: true,
          loading: true,
        },
        {
          error: { message: 'test error' },
          type: 'labelsApi/list/rejected',
        },
      );
      expect(result).toEqual({
        entries: [],
        initialLoad: false,
        loading: false,
      });
      expect(console.warn).toHaveBeenCalledWith(
        'Loading Labels failed. test error',
      );
    });
  });

  describe('labelsApi/list/fulfilled', function () {
    it('should mark loading as no longer in progress', function () {
      const result = labelsApiSlice.reducer(
        {
          entries: [],
          initialLoad: true,
          loading: true,
        },
        {
          type: 'labelsApi/list/fulfilled',
          payload: [],
        },
      );
      expect(result).toEqual({
        entries: [],
        initialLoad: false,
        loading: false,
      });
    });
  });
});

function getStubLabel(patch = {}) {
  return Object.assign(
    {
      id: 1,
      name: 'stub label',
    },
    patch,
  );
}

export {};
