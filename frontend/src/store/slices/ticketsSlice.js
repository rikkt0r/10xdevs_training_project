import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import ticketService from '../../services/ticketService';

const initialState = {
  tickets: [],
  currentTicket: null,
  ticketHistory: [],
  loading: false,
  error: null,
  filters: {
    state: '',
    search: '',
    boardId: null,
  },
};

// Async thunks
export const fetchTickets = createAsyncThunk(
  'tickets/fetchTickets',
  async (params, { rejectWithValue }) => {
    try {
      const response = await ticketService.getTickets(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to fetch tickets' });
    }
  }
);

export const fetchTicket = createAsyncThunk(
  'tickets/fetchTicket',
  async (ticketId, { rejectWithValue }) => {
    try {
      const response = await ticketService.getTicket(ticketId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to fetch ticket' });
    }
  }
);

export const fetchBoardTickets = createAsyncThunk(
  'tickets/fetchBoardTickets',
  async ({ boardId, params }, { rejectWithValue }) => {
    try {
      const response = await ticketService.getBoardTickets(boardId, params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to fetch board tickets' });
    }
  }
);

export const changeTicketState = createAsyncThunk(
  'tickets/changeTicketState',
  async ({ ticketId, newState, comment }, { rejectWithValue }) => {
    try {
      const response = await ticketService.changeTicketState(ticketId, newState, comment);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to change ticket state' });
    }
  }
);

export const fetchTicketHistory = createAsyncThunk(
  'tickets/fetchTicketHistory',
  async (ticketId, { rejectWithValue }) => {
    try {
      const response = await ticketService.getTicketHistory(ticketId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to fetch ticket history' });
    }
  }
);

const ticketsSlice = createSlice({
  name: 'tickets',
  initialState,
  reducers: {
    clearTicketError: (state) => {
      state.error = null;
    },
    clearCurrentTicket: (state) => {
      state.currentTicket = null;
      state.ticketHistory = [];
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = initialState.filters;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch tickets
      .addCase(fetchTickets.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTickets.fulfilled, (state, action) => {
        state.loading = false;
        state.tickets = action.payload;
      })
      .addCase(fetchTickets.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch ticket
      .addCase(fetchTicket.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTicket.fulfilled, (state, action) => {
        state.loading = false;
        state.currentTicket = action.payload;
      })
      .addCase(fetchTicket.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch board tickets
      .addCase(fetchBoardTickets.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBoardTickets.fulfilled, (state, action) => {
        state.loading = false;
        state.tickets = action.payload;
      })
      .addCase(fetchBoardTickets.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Change ticket state
      .addCase(changeTicketState.fulfilled, (state, action) => {
        const index = state.tickets.findIndex(t => t.id === action.payload.id);
        if (index !== -1) {
          state.tickets[index] = action.payload;
        }
        if (state.currentTicket?.id === action.payload.id) {
          state.currentTicket = action.payload;
        }
      })
      // Fetch ticket history
      .addCase(fetchTicketHistory.fulfilled, (state, action) => {
        state.ticketHistory = action.payload;
      });
  },
});

export const { clearTicketError, clearCurrentTicket, setFilters, clearFilters } = ticketsSlice.actions;
export default ticketsSlice.reducer;
