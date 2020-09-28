import React, { useState } from 'react'
import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/Container'

import CodeEditor from '../code-editor'
import { postSubmission } from 'services/submissions'
import TestList from '../tests/tests'
import { Redirect } from 'react-router-dom'

const Submit = ({ taskId }) => {
  const editor = React.createRef()
  const [redirect, setRedirect] = useState(null)

  const submitCode = () => {
    if (editor.current) {
      // hack, this should be done a bit better
      postSubmission(editor.current.props.value, taskId).then((response) => {
        const submissionId = response.id

        setRedirect(`/submission/${taskId}/${submissionId}`)
      })
    }
  }

  if (redirect != null) {
    return ( <Redirect to={redirect} /> )
  } else {
    return (
      <>
        <div>
          <div style={{ height: '30vh' }}>
            <CodeEditor ref={editor} />
          </div>
          <Button onClick={submitCode}>Submit</Button>
        </div>
        <hr />
        <div>
          <Container>
            <TestList refresh={0} taskId={taskId} />
          </Container>
        </div>
  
      </>
    )
  }
}

export default Submit
