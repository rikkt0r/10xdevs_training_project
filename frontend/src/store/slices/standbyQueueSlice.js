import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import standbyQueueService from '../../services/standbyQueueService';

const initialState = {
  items: [],
  currentItem: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchQueueItems = createAsyncThunk(
  'standbyQueue/fetchQueueItems',
  async (params, { rejectWithValue }) => {
    try {
      const response = await standbyQueueService.getQueueItems(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to fetch queue items' });
    }
  }
);

export const fetchQueueItem = createAsyncThunk(
  'standbyQueue/fetchQueueItem',
  async (itemId, { rejectWithValue }) => {
    try {
      const response = await standbyQueueService.getQueueItem(itemId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to fetch queue item' });
    }
  }
);

export const assignToBoard = createAsyncThunk(
  'standbyQueue/assignToBoard',
  async ({ itemId, boardId }, { rejectWithValue }) => {
    try {
      await standbyQueueService.assignToBoard(itemId, boardId);
      return itemId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to assign to board' });
    }
  }
);

export const retryExternal = createAsyncThunk(
  'standbyQueue/retryExternal',
  async (itemId, { rejectWithValue }) => {
    try {
      const response = await standbyQueueService.retryExternal(itemId);
      return { itemId, ...response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to retry external sync' });
    }
  }
);

export const discardItem = createAsyncThunk(
  'standbyQueue/discardItem',
  async (itemId, { rejectWithValue }) => {
    try {
      await standbyQueueService.discardItem(itemId);
      return itemId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to discard item' });
    }
  }
);

const standbyQueueSlice = createSlice({
  name: 'standbyQueue',
  initialState,
  reducers: {
    clearQueueError: (state) => {
      state.error = null;
    },
    clearCurrentItem: (state) => {
      state.currentItem = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch queue items
      .addCase(fetchQueueItems.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchQueueItems.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchQueueItems.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch queue item
      .addCase(fetchQueueItem.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchQueueItem.fulfilled, (state, action) => {
        state.loading = false;
        state.currentItem = action.payload;
      })
      .addCase(fetchQueueItem.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Assign to board
      .addCase(assignToBoard.fulfilled, (state, action) => {
        state.items = state.items.filter(item => item.id !== action.payload);
        if (state.currentItem?.id === action.payload) {
          state.currentItem = null;
        }
      })
      // Discard item
      .addCase(discardItem.fulfilled, (state, action) => {
        state.items = state.items.filter(item => item.id !== action.payload);
        if (state.currentItem?.id === action.payload) {
          state.currentItem = null;
        }
      });
  },
});

export const { clearQueueError, clearCurrentItem } = standbyQueueSlice.actions;
export default standbyQueueSlice.reducer;
