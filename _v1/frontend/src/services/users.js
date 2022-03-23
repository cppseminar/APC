import api from '../app/api'

const verifyResponse = (response) => {
  return response.data
}

const catchError = (error) => {
  return Promise.reject(error.response)
}

export const getUsers = async () => {
  return api.get('/api/users').then(verifyResponse).catch(catchError)
}
