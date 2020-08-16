import { createSlice } from '@reduxjs/toolkit';


export const counterSlice = createSlice({
  name: 'auth',
  initialState: {
    token: "",
  },
  reducers: {
    setAuthToken: (state, action) => {
      state.token =  action.payload
    }
  },
});

export const { setAuthToken } = counterSlice.actions;


export const selectToken = state => {
  return state.auth.token
}

export const authReducer = counterSlice.reducer

