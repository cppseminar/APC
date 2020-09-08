import api from '../app/api'


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
  let params = {}
  if (submissionId) {
    params = { submission: submissionId }
  }
  if (taskId) {
    params = Object.assign(params, { task: taskId })
  }
  return api.get('/api/tests', { params })
    .then(result => result.data)
}

export const getTest = (testId) => {
  return api.get('/api/tests/' + testId).then(result => result.data)
}
