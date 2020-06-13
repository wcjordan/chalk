export interface Todo {
  id: number;
  description: string;
  created_at: string;
}

export interface ApiState<T> {
  entries: T[];
  loading: boolean;
}

export interface ReduxState {
  todosApi: ApiState<Todo>;
}
