import React, { useState } from 'react'
import Button from 'react-bootstrap/Button'

import CodeEditor from '../code-editor'
import { postSubmission } from 'services/submissions'

const Submit = ({ taskId }) => {
  const [value, setValue] = useState('')

  return (
    <>
      <div style={{height: '30vh'}}>
        <CodeEditor onChange={(newValue) => { setValue(newValue) }} />
      </div>
      <Button onClick={() => { postSubmission(value, taskId) }}>Submit</Button>
    </>
  )
}

export default Submit