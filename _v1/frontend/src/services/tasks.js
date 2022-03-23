import api from '../app/api'
import store from '../app/store'
import { getSelectedUser } from '../app/selectors'

const verifyResponse = (response) => {
  return response.data
}

const catchError = (error) => {
  return Promise.reject(error.response)
}

export const getTasks = async () => {
  return api.get('/api/tasks', {
    params: {
      user: getSelectedUser(store.getState())
    }
  }).then(verifyResponse).catch(catchError)
}

export const getTask = async (taskId) => {
  return api.get('/api/tasks/' + taskId, {
    params: {
      user: getSelectedUser(store.getState())
    }
  }).then(verifyResponse).catch(catchError)
}
