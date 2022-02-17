import { ReduxState } from './redux/types';

export const selectFilteredTodos = (state: ReduxState) => {
  // TODO (jordan) optimize w/ set intersection?
  const { filterLabels } = state.workspace;
  if (filterLabels.includes('Unlabeled')) {
    if (filterLabels.length > 1) {
      return [];
    }
    return state.todosApi.entries.filter((todo) => todo.labels.length === 0);
  }

  return state.todosApi.entries.filter((todo) =>
    filterLabels.every((label) => todo.labels.includes(label)),
  );
};

export const selectSelectedPickerLabels = (state: ReduxState) => {
  const labelingTodo = state.todosApi.entries.find(
    (todo) => todo.id === state.workspace.labelTodoId,
  );
  if (labelingTodo) {
    return labelingTodo.labels.reduce(
      (acc: { [label: string]: boolean }, next: string) => {
        acc[next] = true;
        return acc;
      },
      {},
    );
  }

  return {};
};
