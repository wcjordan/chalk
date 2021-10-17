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
  todosApi: ApiState<Todo>;
  workspace: WorkspaceState;
}

export interface WorkspaceState {
  editId: number | null;
  labelPickerVisible: boolean;
  labels: string[];
  selectedLabels: { [label: string]: boolean };
}
