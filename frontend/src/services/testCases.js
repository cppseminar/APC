import pickBy from 'lodash/pickBy'

import api from '../app/api'
import store from '../app/store'

export const getCases = (taskId) => {
  return api.get('/api/cases', {
    params: {
      task: taskId
    }
  }).then(response => response.data)
}

export const submitTest = (testCaseId, submissionId) => {
  return api.post('/api/tests', {
    submissionId,
    testCaseId,
  })
}

export const listTests = ({ submissionId, taskId }) => {
  const params = {
    submission: submissionId,
    task: taskId,
    user: store.getState().auth.email
  }

  return api.get('/api/tests', { 
    params: pickBy(params, v => v != null) 
  })
    .then(result => result.data)
}

export const getTest = (testId) => {
  return api.get('/api/tests/' + testId).then(result => result.data)
}
