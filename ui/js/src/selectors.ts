import { ReduxState, Todo } from './redux/types';

const performFilter = (
  unlabeledFlag: boolean,
  filterLabels: string[],
  preserveIds: number[],
  todo: Todo,
) => {
  if (preserveIds.includes(todo.id)) {
    return true;
  }

  if (unlabeledFlag) {
    return todo.labels.length === 0;
  }
  return filterLabels.every((label) => todo.labels.includes(label));
};

export const selectFilteredTodos = (state: ReduxState) => {
  // TODO (jordan) optimize w/ set intersection?
  const { labelTodoId, filterLabels, todoEditId } = state.workspace;
  const unlabeledFlag = filterLabels.includes('Unlabeled');
  if (unlabeledFlag && filterLabels.length > 1) {
    return [];
  }

  const preserveIds: number[] = [];
  if (labelTodoId) {
    preserveIds.push(labelTodoId);
  }
  if (todoEditId) {
    preserveIds.push(todoEditId);
  }

  return state.todosApi.entries.filter((todo) =>
    performFilter(unlabeledFlag, filterLabels, preserveIds, todo),
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
