import { configureStore } from '@reduxjs/toolkit';
import { ThunkDispatch } from 'redux-thunk';
import rootReducer, { listLabels, listTodos } from './reducers';
import { ReduxState } from './types';

const store = configureStore({
  reducer: rootReducer,
});

const thunkDispatch: ThunkDispatch<
  ReduxState,
  void,
  { state: ReduxState; type: string }
> = store.dispatch;
// TODO dispose
window.setInterval(() => thunkDispatch(listTodos()), 3000);
thunkDispatch(listLabels());

export default store;
