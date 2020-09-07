import React from 'react'
import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/Container'

import CodeEditor from '../code-editor'
import { postSubmission } from 'services/submissions'
import TestList from '../tests/tests'

const Submit = ({ taskId }) => {
  const editor = React.createRef()

  const submitCode = () => {
    if (editor.current) {
      // hack, this should be done a bit better
      postSubmission(editor.current.props.value, taskId)
    }
  }

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

export default Submit
