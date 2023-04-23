import {
  selectActiveWorkContext,
  selectFilteredTodos,
  selectSelectedPickerLabels,
} from './selectors';
import { FILTER_STATUS } from './redux/types';

describe('selectFilteredTodos', function () {
  it('should filter out todos missing any labels', function () {
    const state = {
      workspace: {
        filterLabels: {
          '5 minutes': FILTER_STATUS.Active,
          home: FILTER_STATUS.Active,
        },
      },
      todosApi: {
        entries: [
          {
            id: 1,
            description: 'filtered todo 1',
            labels: ['5 minutes'],
          },
          {
            id: 2,
            description: 'filtered todo 2',
            labels: ['25 minutes', 'home'],
          },
          {
            id: 3,
            description: 'passing todo 1',
            labels: ['5 minutes', 'home'],
          },
          {
            id: 4,
            description: 'passing todo 2',
            labels: ['5 minutes', 'home', 'low-energy'],
          },
        ],
      },
    };

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should not filter out todos missing labels if they are active', function () {
    const state = {
      workspace: {
        editTodoId: 3,
        filterLabels: {
          '5 minutes': FILTER_STATUS.Active,
          home: FILTER_STATUS.Active,
        },
        labelTodoId: 2,
      },
      todosApi: {
        entries: [
          {
            id: 1,
            description: 'filtered todo 1',
            labels: ['5 minutes'],
          },
          {
            id: 2,
            description: 'passing todo 1',
            labels: ['5 minutes'],
          },
          {
            id: 3,
            description: 'passing todo 2',
            labels: ['5 minutes'],
          },
        ],
      },
    };

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should handle when no filters are selected', function () {
    const state = {
      workspace: {
        filterLabels: {},
      },
      todosApi: {
        entries: [
          {
            id: 1,
            description: 'filtered todo 1',
            labels: ['5 minutes'],
          },
          {
            id: 2,
            description: 'filtered todo 2',
            labels: ['25 minutes', 'home'],
          },
          {
            id: 3,
            description: 'passing todo 1',
            labels: ['5 minutes', 'home'],
          },
          {
            id: 4,
            description: 'passing todo 2',
            labels: ['5 minutes', 'home', 'low-energy'],
          },
        ],
      },
    };

    const result = selectFilteredTodos(state);
    expect(result).toEqual(state.todosApi.entries);
  });

  it('should handle when no todos exist', function () {
    const state = {
      workspace: {
        filterLabels: {},
      },
      todosApi: {
        entries: [],
      },
    };

    const result = selectFilteredTodos(state);
    expect(result).toEqual([]);
  });

  it('should filter any labeled todos with the unlabeled filter', function () {
    const state = {
      workspace: {
        filterLabels: {
          Unlabeled: FILTER_STATUS.Active,
        },
      },
      todosApi: {
        entries: [
          {
            id: 1,
            description: 'filtered todo 1',
            labels: ['5 minutes'],
          },
          {
            id: 2,
            description: 'filtered todo 2',
            labels: ['25 minutes', 'home'],
          },
          {
            id: 3,
            description: 'passing todo 1',
            labels: [],
          },
        ],
      },
    };

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should not filter any active todos with the unlabeled filter', function () {
    const state = {
      workspace: {
        editTodoId: 3,
        filterLabels: {
          Unlabeled: FILTER_STATUS.Active,
        },
        labelTodoId: 2,
      },
      todosApi: {
        entries: [
          {
            id: 1,
            description: 'filtered todo 1',
            labels: ['5 minutes'],
          },
          {
            id: 2,
            description: 'passing todo 1',
            labels: ['5 minutes'],
          },
          {
            id: 3,
            description: 'passing todo 2',
            labels: ['5 minutes'],
          },
        ],
      },
    };

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should filter all todos when the unlabeled filter is combined with another filter', function () {
    const state = {
      workspace: {
        filterLabels: {
          Unlabeled: FILTER_STATUS.Active,
          '5 minutes': FILTER_STATUS.Active,
        },
      },
      todosApi: {
        entries: [
          {
            id: 1,
            description: 'filtered todo 1',
            labels: ['5 minutes'],
          },
          {
            id: 2,
            description: 'filtered todo 2',
            labels: ['5 minutes', 'home'],
          },
          {
            id: 3,
            description: 'filtered todo 3',
            labels: [],
          },
        ],
      },
    };

    const result = selectFilteredTodos(state);
    expect(result).toEqual([]);
  });
});

describe('selectSelectedPickerLabels', function () {
  it('should return a map for looking up label presence', function () {
    const state = {
      workspace: {
        labelTodoId: 1,
      },
      todosApi: {
        entries: [
          {
            id: 1,
            labels: ['5 minutes', 'home', 'low-energy'],
          },
        ],
      },
    };

    const result = selectSelectedPickerLabels(state);
    expect(result).toMatchSnapshot();
  });

  it('should return an empty map when no todo is selected', function () {
    const state = {
      workspace: {
        labelTodoId: null,
      },
      todosApi: {
        entries: [
          {
            id: 1,
            labels: ['5 minutes', 'home', 'low-energy'],
          },
        ],
      },
    };

    const result = selectSelectedPickerLabels(state);
    expect(result).toEqual({});
  });

  it('should return an empty map when the selected todo does not exist', function () {
    const state = {
      workspace: {
        labelTodoId: 1,
      },
      todosApi: {
        entries: [],
      },
    };

    const result = selectSelectedPickerLabels(state);
    expect(result).toEqual({});
  });

  it('should return an empty map when no labels exist on the selected todo', function () {
    const state = {
      workspace: {
        labelTodoId: 1,
      },
      todosApi: {
        entries: [
          {
            id: 1,
            labels: [],
          },
        ],
      },
    };

    const result = selectSelectedPickerLabels(state);
    expect(result).toEqual({});
  });
});

describe('selectActiveWorkContext', function () {
  it('should return a work context if labels match', function () {
    const state = {
      workspace: {
        filterLabels: {
          Chalk: FILTER_STATUS.Active,
          '25 minutes': FILTER_STATUS.Active,
        },
      },
    };

    const result = selectActiveWorkContext(state);
    expect(result).toEqual('chalkCoding');
  });

  it('should not return a work context if additional labels are selected', function () {
    const state = {
      workspace: {
        filterLabels: {
          Chalk: FILTER_STATUS.Active,
          '25 minutes': FILTER_STATUS.Active,
          Home: FILTER_STATUS.Active,
        },
      },
    };

    const result = selectActiveWorkContext(state);
    expect(result).toEqual(undefined);
  });

  it('should not return a work context if some of the contexts labels are not selected', function () {
    const state = {
      workspace: {
        filterLabels: {
          Chalk: FILTER_STATUS.Active,
        },
      },
    };

    const result = selectActiveWorkContext(state);
    expect(result).toEqual(undefined);
  });
});

export {};
