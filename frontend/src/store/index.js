import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import boardsReducer from './slices/boardsSlice';
import ticketsReducer from './slices/ticketsSlice';
import standbyQueueReducer from './slices/standbyQueueSlice';
import settingsReducer from './slices/settingsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    boards: boardsReducer,
    tickets: ticketsReducer,
    standbyQueue: standbyQueueReducer,
    settings: settingsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});
