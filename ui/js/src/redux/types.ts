import { ThunkAction } from 'redux-thunk';
import { Action } from '@reduxjs/toolkit';

export interface Todo {
  id: number;
  archived: boolean;
  completed: boolean;
  created_at: number;
  description: string;
}

export interface TodoPatch {
  id: number;
  archived?: boolean;
  completed?: boolean;
  created_at?: number;
  description?: string;
}

export interface ApiState<T> {
  entries: T[];
  loading: boolean;
}

export interface ReduxState {
  todosApi: ApiState<Todo>;
  workspace: WorkspaceState;
}

export interface WorkspaceState {
  editId: number | null;
  uncommittedEdits: Record<number, string>;
}

export type AppThunk = ThunkAction<void, ReduxState, unknown, Action<string>>;
