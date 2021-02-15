import { configureStore } from '@reduxjs/toolkit';
import rootReducer, { listTodos } from './reducers';

const store = configureStore({
  reducer: rootReducer,
});

// TODO dispose
window.setInterval(() => store.dispatch(listTodos()), 3000);

export default store;
