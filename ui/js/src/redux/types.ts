export enum FILTER_STATUS {
  Active = 'ACTIVE',
  Inverted = 'INVERTED',
}

export interface Label {
  id: number;
  name: string;
}

export type NotificationType = 'default' | 'label';

export interface Notification {
  text: string;
  type: NotificationType;
}

export interface NotificationsState {
  notificationQueue: Notification[];
}

export interface Todo {
  id: number;
  archived: boolean;
  completed: boolean;
  created_at: number;
  description: string;
  labels: string[];
  snoozed_until?: string | null;
  version: number;
  [key: string]: boolean | number | string | string[] | null | undefined; // Index signature to allow updates in todosApiSlice#updateTodosFromResponse
}

export interface TodoPatch {
  id: number;
  archived?: boolean;
  completed?: boolean;
  created_at?: number;
  description?: string;
  labels?: string[];
  snoozed_until?: string | null;
  version?: number;
}

export interface NewTodo {
  id?: number;
  archived?: boolean;
  completed?: boolean;
  created_at?: number;
  description?: string;
  labels?: string[];
}

export interface ApiState<T> {
  entries: T[];
  initialLoad: boolean;
  loading: boolean;
}

export interface TodosApiState extends ApiState<Todo> {
  pendingCreates: number[];
  pendingArchives: number[];
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
  snoozedOnly: boolean;
  snoozeTodoId: number | null;
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
