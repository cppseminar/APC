import { createSelector } from '@reduxjs/toolkit'

const isLoggedIn = createSelector(
  state => state.auth.token,
  token => !!token
)

const isAdmin = createSelector(
  state => state.admin.isAdmin,
  isAdmin => isAdmin
)

const getAdmin = createSelector(
  state => state,
  state => isAdmin(state) && (getLoggedUser(state) ?? null)
)

const getStudents = createSelector(
  state => state.users.all,
  users => users.map(x => x.email)
)

const getSelectedUser = createSelector(
  state => state,
  state => state.users.selected || state.auth.email || ''
)

const getLoggedUser = createSelector(
  state => state.auth,
  auth => auth.email || ''
)

export { isLoggedIn, isAdmin, getStudents, getSelectedUser, getLoggedUser, getAdmin }
