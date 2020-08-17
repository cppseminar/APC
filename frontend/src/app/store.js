import { configureStore } from '@reduxjs/toolkit'

import { authReducer } from '../services/auth'

export default configureStore({
  reducer: {
    auth: authReducer
  }
})
