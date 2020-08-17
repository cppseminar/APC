import { createSlice } from '@reduxjs/toolkit'

export const authSlice = createSlice({
  name: 'auth',
  initialState: {
    token: '',
    email: '',
    name: '',
    img: ''
  }, // no user selected
  reducers: {
    setUser: (state, action) => {
      state.token = action.payload.token
      state.email = action.payload.email
      state.name = action.payload.name
      state.img = action.payload.img
    },
    removeUser: (state, action) => {
      state.token = ''
    }
  }
})

export const { setUser, removeUser } = authSlice.actions

export const authReducer = authSlice.reducer
