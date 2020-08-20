import React from 'react'
import Button from 'react-bootstrap/Button'

import CodeEditor from '../code-editor'
import { postSubmission } from 'services/submissions'

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
      <div style={{ height: '30vh' }}>
        <CodeEditor ref={editor} />
      </div>
      <Button onClick={submitCode}>Submit</Button>
    </>
  )
}

export default Submit
