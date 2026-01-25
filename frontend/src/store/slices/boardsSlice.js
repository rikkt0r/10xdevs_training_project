import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import boardService from '../../services/boardService';

const initialState = {
  boards: [],
  currentBoard: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchBoards = createAsyncThunk(
  'boards/fetchBoards',
  async (_, { rejectWithValue }) => {
    try {
      const data = await boardService.getBoards();
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to fetch boards' });
    }
  }
);

export const fetchBoard = createAsyncThunk(
  'boards/fetchBoard',
  async (boardId, { rejectWithValue }) => {
    try {
      const data = await boardService.getBoard(boardId);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to fetch board' });
    }
  }
);

export const createBoard = createAsyncThunk(
  'boards/createBoard',
  async (boardData, { rejectWithValue }) => {
    try {
      const data = await boardService.createBoard(boardData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to create board' });
    }
  }
);

export const updateBoard = createAsyncThunk(
  'boards/updateBoard',
  async ({ boardId, boardData }, { rejectWithValue }) => {
    try {
      const data = await boardService.updateBoard(boardId, boardData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to update board' });
    }
  }
);

export const archiveBoard = createAsyncThunk(
  'boards/archiveBoard',
  async (boardId, { rejectWithValue }) => {
    try {
      const data = await boardService.archiveBoard(boardId);
      return { boardId, ...data };
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to archive board' });
    }
  }
);

export const deleteBoard = createAsyncThunk(
  'boards/deleteBoard',
  async (boardId, { rejectWithValue }) => {
    try {
      await boardService.deleteBoard(boardId);
      return boardId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to delete board' });
    }
  }
);

const boardsSlice = createSlice({
  name: 'boards',
  initialState,
  reducers: {
    clearBoardError: (state) => {
      state.error = null;
    },
    clearCurrentBoard: (state) => {
      state.currentBoard = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch boards
      .addCase(fetchBoards.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBoards.fulfilled, (state, action) => {
        state.loading = false;
        state.boards = action.payload;
      })
      .addCase(fetchBoards.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch board
      .addCase(fetchBoard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBoard.fulfilled, (state, action) => {
        state.loading = false;
        state.currentBoard = action.payload;
      })
      .addCase(fetchBoard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Create board
      .addCase(createBoard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createBoard.fulfilled, (state, action) => {
        state.loading = false;
        state.boards.push(action.payload);
      })
      .addCase(createBoard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update board
      .addCase(updateBoard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateBoard.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.boards.findIndex(b => b.id === action.payload.id);
        if (index !== -1) {
          state.boards[index] = action.payload;
        }
        if (state.currentBoard?.id === action.payload.id) {
          state.currentBoard = action.payload;
        }
      })
      .addCase(updateBoard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Archive board
      .addCase(archiveBoard.fulfilled, (state, action) => {
        const index = state.boards.findIndex(b => b.id === action.payload.boardId);
        if (index !== -1) {
          state.boards[index].archived = true;
        }
      })
      // Delete board
      .addCase(deleteBoard.fulfilled, (state, action) => {
        state.boards = state.boards.filter(b => b.id !== action.payload);
        if (state.currentBoard?.id === action.payload) {
          state.currentBoard = null;
        }
      });
  },
});

export const { clearBoardError, clearCurrentBoard } = boardsSlice.actions;
export default boardsSlice.reducer;
