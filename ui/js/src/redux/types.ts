export interface Todo {
  id: number | null;
  created_at: number;
  description: string;
}

export interface ApiState<T> {
  entries: T[];
  loading: boolean;
}

export interface ReduxState {
  todosApi: ApiState<Todo>;
}
