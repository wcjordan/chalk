import '../__mocks__/matchMediaMock';
import configureMockStore from 'redux-mock-store';
import fetchMock from 'fetch-mock-jest';
import thunk from 'redux-thunk';
import labelsApiSlice, { getLabelsApi, listLabels } from './labelsApiSlice';

const mockStore = configureMockStore([thunk]);

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

    const store = mockStore({ labelsApi: { loading: false } });
    await store.dispatch(listLabels());

    const actions = store.getActions();
    expect(actions.length).toEqual(2);

    // Verify the pending handler is called based on the patch argument
    const pendingAction = actions[0];
    expect(pendingAction.type).toEqual('labelsApi/list/pending');

    // Verify the fulfilled handler is called with the returned label
    const fulfilledAction = actions[1];
    expect(fulfilledAction.payload).toEqual(stubLabels);
    expect(fulfilledAction.type).toEqual('labelsApi/list/fulfilled');

    // Verify we make the server request
    expect(fetchMock).toBeDone();
  });

  it('should do nothing if labels are already loading', async function () {
    fetchMock.mock('*', 200);
    const store = mockStore({ labelsApi: { loading: true } });
    await store.dispatch(listLabels());

    const actions = store.getActions();
    expect(actions.length).toEqual(0);

    // Verify we make the server request
    expect(fetchMock).not.toHaveFetched('*');
  });
});

describe('labelsApiSlice reducer', function () {
  const initialState = {
    entries: [],
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
          loading: true,
        },
        {
          error: { message: 'test error' },
          type: 'labelsApi/list/rejected',
        },
      );
      expect(result).toEqual({
        entries: [],
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
          loading: true,
        },
        {
          type: 'labelsApi/list/fulfilled',
          payload: [],
        },
      );
      expect(result).toEqual({
        entries: [],
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
