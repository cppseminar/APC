import React, { useState, useRef } from 'react'
import Editor from '@monaco-editor/react'

const CodeEditor = () => {
  const [isEditorReady, setIsEditorReady] = useState(false)
  const valueGetter = useRef()

  const handleEditorDidMount = (value) => {
    valueGetter.current = value
    setIsEditorReady(true)
  }

  const handleShowValue = () => {
    console.log(valueGetter.current())
  }

  return (
    <>
      <button onClick={handleShowValue} disabled={!isEditorReady}>
        Show value
      </button>
      <Editor height='30vh' width='90vw' language='cpp' editorDidMount={handleEditorDidMount} />
    </>
  )
}

export default CodeEditor
