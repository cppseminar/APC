import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import isEmpty from 'lodash/isEmpty'

import CodeEditor from '../code-editor'

import { getSubmission } from 'services/submissions'

const Submission = () => {
  const [submission, setSubmission] = useState({})

  const { submissionId } = useParams()

  useEffect(() => {
    getSubmission(submissionId).then((val) => setSubmission(val)).catch(setSubmission(null))
  }, [submissionId])

  console.log(submission)

  return isEmpty(submission) ? 'Error!' : (
    <div style={{ border: '1px solid green' }}>
      {submission.files.map(x => {
        return (
          <div key={x._id}>
            <h2>{x.fileName}</h2>
            <div style={{ width: '100%', height: '30vh' }}>
              <CodeEditor readOnly defValue={x.fileContent} />
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default Submission
