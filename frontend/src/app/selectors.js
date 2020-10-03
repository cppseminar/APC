import { createSelector } from '@reduxjs/toolkit'

const isLoggedIn = createSelector(
  state => state.auth.token,
  token => !!token
)

export { isLoggedIn }
