import { configureStore } from '@reduxjs/toolkit'

import { authReducer } from './reducers/auth'

export default configureStore({
  reducer: {
    auth: authReducer
  }
})
