import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
// Import slices (will be created later)
// import boardsReducer from './slices/boardsSlice';
// import ticketsReducer from './slices/ticketsSlice';
// import inboxesReducer from './slices/inboxesSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    // boards: boardsReducer,
    // tickets: ticketsReducer,
    // inboxes: inboxesReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});
