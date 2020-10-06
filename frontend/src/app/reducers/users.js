import { createSlice } from '@reduxjs/toolkit'

export const usersSlice = createSlice({
  name: 'users',
  initialState: {
    all: [],
    selected: ''
  },
  reducers: {
    setUsers: (state, action) => {
      state.all = action.payload
    },
    selectUser: (state, action) => {
      state.selected = action.payload
    }
  }
})

export const { setUsers, selectUser } = usersSlice.actions

export const usersReducer = usersSlice.reducer
