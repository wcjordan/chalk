import { configureStore } from '@reduxjs/toolkit';
import rootReducer, { listLabels, listTodos } from './reducers';

const store = configureStore({
  reducer: rootReducer,
});

// TODO dispose
window.setInterval(() => store.dispatch(listTodos()), 3000);
store.dispatch(listLabels());

export default store;
