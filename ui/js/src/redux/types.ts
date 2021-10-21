export interface Label {
  id: number;
  name: string;
}

export interface Todo {
  id: number;
  archived: boolean;
  completed: boolean;
  created_at: number;
  description: string;
  label_set: string[];
}

export interface TodoPatch {
  id: number;
  archived?: boolean;
  completed?: boolean;
  created_at?: number;
  description?: string;
  label_set?: string[];
}

export interface NewTodo {
  id?: number;
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
  labelsApi: ApiState<Label>;
  todosApi: ApiState<Todo>;
  workspace: WorkspaceState;
}

export interface WorkspaceState {
  editId: number | null;
  labelTodoId: number | null;
}
