import React from 'react'
import AceEditor from 'react-ace'

import 'ace-builds/src-noconflict/mode-c_cpp'
import 'ace-builds/src-noconflict/theme-monokai'

const CodeEditor = ({ onChange, readOnly, value }) => {
  console.log(onChange, readOnly, value)
  return (
    <AceEditor 
      height='100%'
      width='100%'
      mode='c_cpp'
      theme='monokai'
      placeholder='// Place your code here...'
      onChange={onChange ?? (() => {})}
      value={value ?? ''}
      readOnly={readOnly ?? false}
    />
  )
}

export default CodeEditor
