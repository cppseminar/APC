import { createSlice } from '@reduxjs/toolkit'

export const authSlice = createSlice({
  name: 'auth',
  initialState: {
    token: '',
    email: '',
    name: '',
    img: '',
    firstSilentLoginRunning: true,
    isAdmin: false
  },
  reducers: {
    setUser: (state, action) => {
      return action.payload
    },
    removeUser: (state) => {
      state.token = ''
    },
    refreshToken: (state, action) => {
      state.token = action.payload
    },
    firstSilentLoginFinished: (state) => {
      state.firstSilentLoginRunning = false
    }
  }
})

export const { setUser, removeUser, firstSilentLoginFinished, refreshToken } = authSlice.actions

export const authReducer = authSlice.reducer
