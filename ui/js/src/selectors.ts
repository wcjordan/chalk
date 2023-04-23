import { FILTER_STATUS, ReduxState, Todo } from './redux/types';
import { workContexts } from './redux/workspaceSlice';

const performFilter = (
  labeledFlag: boolean,
  unlabeledFlag: boolean,
  activeFilters: string[],
  invertedFilters: string[],
  preserveIds: number[],
  todo: Todo,
) => {
  if (preserveIds.includes(todo.id)) {
    return true;
  }

  if (unlabeledFlag) {
    return todo.labels.length === 0;
  }

  return (
    (!labeledFlag || todo.labels.length > 0) && // Require labels if labeledFlag is true
    activeFilters.every((label) => todo.labels.includes(label)) && // Require every active filter
    invertedFilters.every((label) => !todo.labels.includes(label)) // Disallow every inverted filter
  );
};

export const selectFilteredTodos = (state: ReduxState) => {
  // TODO (jordan) optimize w/ set intersection?
  const { editTodoId, filterLabels, labelTodoId } = state.workspace;
  const labeledFlag = filterLabels['Unlabeled'] === FILTER_STATUS.Inverted;
  const unlabeledFlag = filterLabels['Unlabeled'] === FILTER_STATUS.Active;

  // Filter down to active filters excluding 'Unlabeled'
  const activeFilters = Object.keys(filterLabels).filter(
    (labelKey) =>
      labelKey !== 'Unlabeled' &&
      filterLabels[labelKey] === FILTER_STATUS.Active,
  );
  // Filter down to inverted filters excluding 'Unlabeled'
  const invertedFilters = Object.keys(filterLabels).filter(
    (labelKey) =>
      labelKey !== 'Unlabeled' &&
      filterLabels[labelKey] === FILTER_STATUS.Inverted,
  );

  if (unlabeledFlag && activeFilters.length > 0) {
    return [];
  }

  // Preserve todo items being edited or labeled even if they don't match the filters
  const preserveIds: number[] = [];
  if (labelTodoId) {
    preserveIds.push(labelTodoId);
  }
  if (editTodoId) {
    preserveIds.push(editTodoId);
  }

  return state.todosApi.entries.filter((todo) =>
    performFilter(
      labeledFlag,
      unlabeledFlag,
      activeFilters,
      invertedFilters,
      preserveIds,
      todo,
    ),
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

export const selectActiveWorkContext = (state: ReduxState) => {
  const { filterLabels } = state.workspace;
  return Object.keys(workContexts).find((workContext) => {
    const labels = workContexts[workContext].labels;
    const labelKeys = Object.keys(labels);
    const sizeMatch = labelKeys.length === Object.keys(filterLabels).length;
    return (
      sizeMatch &&
      labelKeys.every((labelKey) => labels[labelKey] === filterLabels[labelKey])
    );
  });
};
