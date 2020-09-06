import api from '../app/api'


export const getCases = (taskId) => {
  return api.get('/api/cases', {params : {
    task: taskId
  }}).then(response => response.data)
}

export const submitTest = (testCaseId, submissionId) => {
  return api.post('/api/tests', {
    submissionId,
    testCaseId,
  })
}
