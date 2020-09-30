import api from '../app/api'
import store from '../app/store'

const verifyResponse = (response) => {
  return response.data
}

const catchError = (response) => {
  return null
}

export const postSubmission = async (content, taskId) => {
  return api.post('/api/submissions', {
    files: [
      {
        fileName: 'main.cpp',
        fileContent: content
      }
    ],
    taskId
  }).then(verifyResponse).catch(catchError)
}

export const getSubmissions = async (taskId) => {
  return api.get('/api/submissions', {
    params: {
      task: taskId,
      user: store.getState().auth.email || ''
    }
  }).then(verifyResponse).catch(catchError)
}

export const getSubmission = async (submissionId) => {
  return api.get('/api/submissions/' + submissionId).then(verifyResponse).catch(catchError)
}
