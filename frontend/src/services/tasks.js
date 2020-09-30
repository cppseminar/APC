import api from '../app/api'
import store from '../app/store'

const verifyResponse = (response) => {
  return response.data
}

const catchError = (error) => {
  return Promise.reject(error.response)
}

export const getTasks = async () => {
  return api.get('/api/tasks', {
    params: {
      user: store.getState().auth.email || ''
    }
  }).then(verifyResponse).catch(catchError)
}

export const getTask = async (taskId) => {
  return api.get('/api/tasks/' + taskId, {
    params: {
      user: store.getState().auth.email || ''
    }
  }).then(verifyResponse).catch(catchError)
}
