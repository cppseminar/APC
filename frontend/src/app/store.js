import { configureStore } from '@reduxjs/toolkit';
import counterReducer from '../features/counter/counterSlice';
import {authReducer} from 'services/auth'

export default configureStore({
  reducer: {
    counter: counterReducer,
    auth: authReducer,
  },
});
