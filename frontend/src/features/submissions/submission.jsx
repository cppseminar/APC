import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'

import CodeEditor from '../code-editor'
import LoadingOverlay from '../loading-overlay'

import { getSubmission } from 'services/submissions'

const Submission = () => {
  const [submission, setSubmission] = useState({})
  const [state, setState] = useState('loading')

  const { submissionId } = useParams()

  useEffect(() => {
    setState('loading')

    getSubmission(submissionId)
      .then((val) => {
        setSubmission(val)
        setState('loaded')
      })
      .catch(() => setState('error'))
  }, [submissionId])

  switch (state) {
    case 'loading': return ( <LoadingOverlay /> )
    case 'loaded': return (
      <div>
        <h2>Your submitted files</h2>
        {submission.files.map(x => {
          return (
            <div key={x.id + x.fileName}>
              <h3>{x.fileName}</h3>
              <div style={{ width: '100%', height: '70vh' }}>
                <CodeEditor readOnly defValue={x.fileContent} />
              </div>
            </div>
          )
        })}
      </div>
    )
    case 'error':
    default: return (
      <p>
        Submission cannot loaded, please make sure you are logged on and the path is right.
      </p>
    )
  }
}

export default Submission
