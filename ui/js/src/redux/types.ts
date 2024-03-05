export enum FILTER_STATUS {
  Active = 'ACTIVE',
  Inverted = 'INVERTED',
}

export interface Label {
  id: number;
  name: string;
}

export interface NotificationsState {
  notificationQueue: string[];
}

export interface Todo {
  id: number;
  archived: boolean;
  completed: boolean;
  created_at: number;
  description: string;
  labels: string[];
}

export interface TodoPatch {
  id: number;
  archived?: boolean;
  completed?: boolean;
  created_at?: number;
  description?: string;
  labels?: string[];
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
  initialLoad: boolean;
  loading: boolean;
}

export interface FilterState {
  [index: string]: FILTER_STATUS;
}

export interface WorkContext {
  displayName: string;
  labels: FilterState;
}

export interface WorkspaceState {
  // CSRF token is only set here for mobile auth
  // For web we extract the CSRF token from cookies
  csrfToken: string | null;
  editTodoId: number | null;
  filterLabels: FilterState;
  labelTodoId: number | null;
  loggedIn: boolean;
  showCompletedTodos: boolean;
  showLabelFilter: boolean;
}

export interface MoveTodoOperation {
  position: 'after' | 'before';
  relative_id: number;
  todo_id: number;
}

export interface ShortcutOperation {
  type: 'EDIT_TODO' | 'MOVE_TODO';
  payload: TodoPatch | MoveTodoOperation;
  generation: number;
}

export interface ShortcutState {
  operations: ShortcutOperation[];
  latestGeneration: number;
}
