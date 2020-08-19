import React, { useState, useRef } from 'react'
import AceEditor from 'react-ace'

import 'ace-builds/src-noconflict/mode-c_cpp'
import 'ace-builds/src-noconflict/theme-monokai'

const CodeEditor = () => {
  const [value, setValue] = useState('')
  const valueGetter = useRef()

  return (
    <>
      <AceEditor 
        height='30vh'
        width='90vw'
        mode='c_cpp'
        theme='monokai'
        defaultValue={value}
        placeholder='// Place your code here...'
        onChange={(newValue) => { setValue(newValue) }}
      />
    </>
  )
}

export default CodeEditor
