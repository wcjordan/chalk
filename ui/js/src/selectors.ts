import { createSelector } from '@reduxjs/toolkit';
import { RootState } from './redux/store';
import {
  FILTER_STATUS,
  MoveTodoOperation,
  Todo,
  TodoPatch,
} from './redux/types';
import { workContexts } from './redux/workspaceSlice';

const selectEditTodoId = (state: RootState) => state.workspace.editTodoId;
const selectFilterLabels = (state: RootState) => state.workspace.filterLabels;
const selectLabelTodoId = (state: RootState) => state.workspace.labelTodoId;
const selectShortcutOperations = (state: RootState) =>
  state.shortcuts.operations;
const selectShowCompletedTodos = (state: RootState) =>
  state.workspace.showCompletedTodos;
const selectTodoApiEntries = (state: RootState) => state.todosApi.entries;
const selectLabelApiEntries = (state: RootState) => state.labelsApi.entries;

export const selectShortcuttedTodoEntries = createSelector(
  [selectShortcutOperations, selectTodoApiEntries],
  (shortcutOperations, todoApiEntries) => {
    if (shortcutOperations.length === 0) {
      return todoApiEntries;
    }

    const shortcuttedTodoEntries = Array.from(todoApiEntries);
    for (const op of shortcutOperations) {
      if (op.type === 'EDIT_TODO') {
        const patch = op.payload as TodoPatch;
        const todoIdx = shortcuttedTodoEntries.findIndex(
          (todo) => todo && todo.id === patch.id,
        );
        if (todoIdx !== -1) {
          const origTodo = shortcuttedTodoEntries[todoIdx];
          const shortcuttedTodo = Object.assign({}, origTodo, patch);
          shortcuttedTodoEntries[todoIdx] = shortcuttedTodo;
        } else {
          console.warn(`Unable to find todo with shortcut: ${patch}`);
        }
      } else if (op.type === 'MOVE_TODO') {
        const moveOp = op.payload as MoveTodoOperation;
        const todoIdx = shortcuttedTodoEntries.findIndex(
          (todo) => todo && todo.id === moveOp.todo_id,
        );

        if (todoIdx === -1) {
          console.warn(
            `Unable to find todo with shortcut: ${JSON.stringify(moveOp)}`,
          );
          continue;
        }

        // Remove the element to move
        const todo = shortcuttedTodoEntries[todoIdx];
        shortcuttedTodoEntries.splice(todoIdx, 1);

        // Insert the element at the new position
        let relativeIdx = shortcuttedTodoEntries.findIndex(
          (todo) => todo.id === moveOp.relative_id,
        );
        if (moveOp.position === 'after') {
          relativeIdx++;
        }
        shortcuttedTodoEntries.splice(relativeIdx, 0, todo);
      } else {
        throw new Error(`Unexpected shortcut operation type: ${op.type}`);
      }
    }
    return shortcuttedTodoEntries;
  },
);

const performFilter = (
  labeledFlag: boolean,
  unlabeledFlag: boolean,
  activeFilters: string[],
  invertedFilters: string[],
  showCompletedTodos: boolean,
  preserveIds: number[],
  todo: Todo,
) => {
  if (preserveIds.includes(todo.id)) {
    return true;
  }

  if (!showCompletedTodos && todo.completed) {
    return false;
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

export const selectFilteredTodos = createSelector(
  [
    selectShortcuttedTodoEntries,
    selectEditTodoId,
    selectFilterLabels,
    selectLabelTodoId,
    selectShowCompletedTodos,
  ],
  (
    todoApiEntries,
    editTodoId,
    filterLabels,
    labelTodoId,
    showCompletedTodos,
  ) => {
    // TODO (jordan) optimize w/ set intersection?
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

    return todoApiEntries.filter((todo) =>
      performFilter(
        labeledFlag,
        unlabeledFlag,
        activeFilters,
        invertedFilters,
        showCompletedTodos,
        preserveIds,
        todo,
      ),
    );
  },
);

export const selectActiveFilterLabels = createSelector(
  [selectFilterLabels],
  (filterLabels) => {
    // Extract active filters excluding 'Unlabeled' (which is virtual)
    return Object.keys(filterLabels).filter(
      (labelKey) =>
        labelKey !== 'Unlabeled' &&
        filterLabels[labelKey] === FILTER_STATUS.Active,
    );
  },
);

export const selectSelectedPickerLabels = createSelector(
  [selectTodoApiEntries, selectLabelTodoId],
  (todoApiEntries, labelTodoId) => {
    const labelingTodo = todoApiEntries.find((todo) => todo.id === labelTodoId);
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
  },
);

export const selectActiveWorkContext = createSelector(
  [selectFilterLabels],
  (filterLabels) => {
    return Object.keys(workContexts).find((workContext) => {
      const labels = workContexts[workContext].labels;
      const labelKeys = Object.keys(labels);
      const sizeMatch = labelKeys.length === Object.keys(filterLabels).length;
      return (
        sizeMatch &&
        labelKeys.every(
          (labelKey) => labels[labelKey] === filterLabels[labelKey],
        )
      );
    });
  },
);

export const selectIsLoading = (state: RootState) => {
  return state.labelsApi.initialLoad || state.todosApi.initialLoad;
};

export const selectLabelNames = createSelector(
  [selectLabelApiEntries],
  (labels) => labels.map((label) => label.name),
);
