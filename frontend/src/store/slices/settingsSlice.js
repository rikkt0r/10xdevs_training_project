import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import settingsService from '../../services/settingsService';

const initialState = {
  profile: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchProfile = createAsyncThunk(
  'settings/fetchProfile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await settingsService.getProfile();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to fetch profile' });
    }
  }
);

export const updateProfile = createAsyncThunk(
  'settings/updateProfile',
  async (profileData, { rejectWithValue }) => {
    try {
      const response = await settingsService.updateProfile(profileData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to update profile' });
    }
  }
);

export const changePassword = createAsyncThunk(
  'settings/changePassword',
  async ({ currentPassword, newPassword }, { rejectWithValue }) => {
    try {
      const response = await settingsService.changePassword(currentPassword, newPassword);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to change password' });
    }
  }
);

export const suspendAccount = createAsyncThunk(
  'settings/suspendAccount',
  async ({ suspensionMessage, password }, { rejectWithValue }) => {
    try {
      const response = await settingsService.suspendAccount(suspensionMessage, password);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || { message: 'Failed to suspend account' });
    }
  }
);

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    clearSettingsError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch profile
      .addCase(fetchProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profile = action.payload;
      })
      .addCase(fetchProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update profile
      .addCase(updateProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profile = action.payload;
      })
      .addCase(updateProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Change password
      .addCase(changePassword.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(changePassword.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(changePassword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearSettingsError } = settingsSlice.actions;
export default settingsSlice.reducer;
