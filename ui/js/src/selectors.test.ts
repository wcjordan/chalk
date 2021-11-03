import { selectFilteredTodos, selectSelectedPickerLabels } from './selectors';

describe('selectFilteredTodos', function () {
  it('should filter out todos missing any labels', function () {
    const state = {
      workspace: {
        filterLabels: ['5 minutes', 'home'],
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

  it('should handle when no filters are selected', function () {
    const state = {
      workspace: {
        filterLabels: [],
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
        filterLabels: [],
      },
      todosApi: {
        entries: [],
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

export {};
