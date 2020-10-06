import { configureStore } from '@reduxjs/toolkit'

import { authReducer } from './reducers/auth'
import { adminReducer } from './reducers/admin'
import { usersReducer } from './reducers/users'

export default configureStore({
  reducer: {
    auth: authReducer,
    admin: adminReducer,
    users: usersReducer
  },
  preloadedState: {
    admin: {
      isAdmin: !!localStorage.getItem('isAdmin')
    }
  }
})
