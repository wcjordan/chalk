import {
  selectActiveWorkContext,
  selectFilteredTodos,
  selectSelectedPickerLabels,
} from './selectors';
import { FILTER_STATUS } from './redux/types';

function selectFilteredTodosHelper(activeLabels, invertedLabels, todos) {
  const filterLabels = {};
  activeLabels.forEach((label) => {
    filterLabels[label] = FILTER_STATUS.Active;
  });
  invertedLabels.forEach((label) => {
    filterLabels[label] = FILTER_STATUS.Inverted;
  });

  let id = 1;
  const entries = [];
  Object.keys(todos).forEach((description) => {
    entries.push({
      id: id++,
      description,
      labels: todos[description],
    });
  });

  return {
    workspace: {
      filterLabels,
    },
    shortcuts: {
      operations: [],
    },
    todosApi: {
      entries,
    },
  };
}

describe('selectFilteredTodos', function () {
  it('should filter out todos missing any labels', function () {
    const activeFilters = ['5 minutes', 'home'];
    const state = selectFilteredTodosHelper(activeFilters, [], {
      'filtered todo 1': ['5 minutes'],
      'filtered todo 2': ['25 minutes', 'home'],
      'passing todo 1': ['5 minutes', 'home'],
      'passing todo 2': ['5 minutes', 'home', 'low-energy'],
    });

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should not filter out todos missing labels if they are actively being modified', function () {
    const activeFilters = ['5 minutes', 'home'];
    const state = selectFilteredTodosHelper(activeFilters, [], {
      'filtered todo 1': ['5 minutes'],
      'passing todo 1': ['5 minutes'],
      'passing todo 2': ['5 minutes'],
    });
    state.workspace.editTodoId = 3;
    state.workspace.labelTodoId = 2;

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should handle when no filters are selected', function () {
    const state = selectFilteredTodosHelper([], [], {
      'filtered todo 1': ['5 minutes'],
      'filtered todo 2': ['25 minutes', 'home'],
      'passing todo 1': ['5 minutes', 'home'],
      'passing todo 2': ['5 minutes', 'home', 'low-energy'],
    });

    const result = selectFilteredTodos(state);
    expect(result).toEqual(state.todosApi.entries);
  });

  it('should handle when no todos exist', function () {
    const state = selectFilteredTodosHelper([], [], {});
    const result = selectFilteredTodos(state);
    expect(result).toEqual([]);
  });

  it('should filter any labeled todos with the unlabeled filter', function () {
    const activeFilters = ['Unlabeled'];
    const state = selectFilteredTodosHelper(activeFilters, [], {
      'filtered todo 1': ['5 minutes'],
      'filtered todo 2': ['25 minutes', 'home'],
      'passing todo 1': [],
    });

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should not filter any active todos with the unlabeled filter', function () {
    const activeFilters = ['Unlabeled'];
    const state = selectFilteredTodosHelper(activeFilters, [], {
      'filtered todo 1': ['5 minutes'],
      'passing todo 1': ['5 minutes'],
      'passing todo 2': ['5 minutes'],
    });
    state.workspace.editTodoId = 3;
    state.workspace.labelTodoId = 2;

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should filter all todos when the unlabeled filter is combined with another filter', function () {
    const activeFilters = ['Unlabeled', '5 minutes'];
    const state = selectFilteredTodosHelper(activeFilters, [], {
      'filtered todo 1': ['5 minutes'],
      'filtered todo 2': ['5 minutes', 'home'],
      'filtered todo 3': [],
    });

    const result = selectFilteredTodos(state);
    expect(result).toEqual([]);
  });

  it('should filter todos missing any labels even when unlabeled is inverted', function () {
    const activeFilters = ['home'];
    const invertedFilters = ['Unlabeled'];
    const state = selectFilteredTodosHelper(activeFilters, invertedFilters, {
      'filtered todo 1': ['5 minutes'],
      'filtered todo 2': ['5 minutes', 'home'],
      'filtered todo 3': [],
    });

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should filter out todos which have an inverted filters label', function () {
    const invertedFilters = ['5 minutes'];
    const state = selectFilteredTodosHelper([], invertedFilters, {
      'filtered todo 1': ['5 minutes'],
      'passing todo 1': ['25 minutes', 'home'],
      'passing todo 2': ['25 minutes', 'work'],
    });

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should filter out todos which have any inverted filters label', function () {
    const invertedFilters = ['5 minutes', 'home'];
    const state = selectFilteredTodosHelper([], invertedFilters, {
      'filtered todo 1': ['5 minutes'],
      'filtered todo 2': ['25 minutes', 'home'],
      'passing todo 1': ['25 minutes', 'work'],
    });

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should show labeled items without a specific label when unlabeled and a label are both inverted', function () {
    const invertedFilters = ['Unlabeled', '5 minutes'];
    const state = selectFilteredTodosHelper([], invertedFilters, {
      'filtered todo 1': ['5 minutes'],
      'filtered todo 2': [],
      'passing todo 1': ['25 minutes', 'work'],
    });

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
  });

  it('should combine active and inverted filters to find items with one label and without another', function () {
    const activeFilters = ['home'];
    const invertedFilters = ['5 minutes'];
    const state = selectFilteredTodosHelper(activeFilters, invertedFilters, {
      'filtered todo 1': ['5 minutes', 'home'],
      'filtered todo 2': ['work'],
      'filtered todo 3': [],
      'passing todo 1': ['25 minutes', 'home'],
    });

    const result = selectFilteredTodos(state);
    expect(result).toMatchSnapshot();
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
          vague: FILTER_STATUS.Active,
        },
      },
    };

    const result = selectActiveWorkContext(state);
    expect(result).toEqual('chalkPlanning');
  });

  it('should not return a work context if additional labels are selected', function () {
    const state = {
      workspace: {
        filterLabels: {
          Chalk: FILTER_STATUS.Active,
          vague: FILTER_STATUS.Active,
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
