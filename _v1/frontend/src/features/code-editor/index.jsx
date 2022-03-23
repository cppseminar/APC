import React, { useState } from 'react'
import AceEditor from 'react-ace'

import 'ace-builds/src-noconflict/mode-c_cpp'
import 'ace-builds/src-noconflict/theme-monokai'

const CodeEditor = React.forwardRef(({ readOnly, defValue }, ref) => {
  const [value, setValue] = useState(defValue)

  return (
    <>
      <AceEditor
        ref={ref}
        height='100%'
        width='100%'
        mode='c_cpp'
        theme='monokai'
        placeholder='// Place your code here...'
        onChange={(newValue) => { setValue(newValue) }}
        value={value ?? ''}
        readOnly={readOnly ?? false}
        fontSize='1rem'
      />
    </>
  )
})

export default CodeEditor
