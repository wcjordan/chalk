import { ThunkAction } from 'redux-thunk';
import { Action } from '@reduxjs/toolkit';

export interface Todo {
  id: number;
  created_at: number;
  description: string;
}

export interface TodoPatch {
  id: number;
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
}

export type AppThunk = ThunkAction<void, ReduxState, unknown, Action<string>>;
