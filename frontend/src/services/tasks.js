import api from '../app/api'

const verifyResponse = (response) => {
  return response.data
}

const catchError = (response) => {
  console.log(response)
}

export const getTasks = async () => {
  return api.get('/api/tasks').then(verifyResponse).catch(catchError)
}

export const getTask = async (taskId) => {
  return api.get('/api/tasks/' + taskId).then(verifyResponse).catch(catchError)
}
