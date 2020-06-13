import { configureStore } from '@reduxjs/toolkit';
import rootReducer, { fetchTodos } from './reducers';

const store = configureStore({
  reducer: rootReducer,
});

// TODO dispose
window.setInterval(() => store.dispatch(fetchTodos()), 1000);

export default store;
