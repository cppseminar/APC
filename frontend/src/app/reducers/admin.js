import { createSlice } from '@reduxjs/toolkit'

export const adminSlice = createSlice({
  name: 'admin',
  initialState: {
    isAdmin: false
  }
})

export const adminReducer = adminSlice.reducer
