import React, { useState } from 'react'

import './App.css'
import api from './app/api'

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from 'react-router-dom'

import GoogleLogin, { CallbackPage } from './features/google-login/button'
import CodeEditor from './features/code-editor'

import Tasks from './pages/tasks'

if (process.env.NODE_ENV === 'development') {
  console.log('Current environment ', process.env)
}

const Submissions = (props) => {
  const [url, setUrl] = useState('/api/submissions/')
  const [response, setResponse] = useState('')
  const [code, setCode] = useState(0)

  const submit = () => {
    api.get(url).then(response => {
      setCode(response.status)
      return response.data
    }).then(json => setResponse(JSON.stringify(json, null, 2))).catch((obj) => {
      setResponse('Some error')
      console.log(obj)
    })
  }

  return (
    <>
      <div>
      Set url:
        <input type='text' onChange={(event) => setUrl(event.target.value)} value={url} />
      </div>
      <div>
        <button onClick={submit}>Request!</button>
      </div>
      <div style={{ border: '1px solid black' }}>
        <p>Response code {code}</p>
        <pre style={{ border: '1px solid blue', textAlign: 'left' }}>
          {response}
        </pre>
      </div>
    </>
  )
}

const App = () => {
  return (
    <div className='App'>
      <Router>
        <Switch>
          <Route path='/.auth/google/login'>
            <CallbackPage />
          </Route>
          <Route path='/task/'>
            <Tasks />
          </Route>
          <Route path='/'>
            <header className='App-header'>
              <h3><Link to='/task'>Tasks</Link></h3>
              <p>But first login!</p>

              <GoogleLogin />
              <CodeEditor />
              <hr style={{ width: '10em' }} />

              <Submissions />

            </header>
          </Route>

        </Switch>
      </Router>
    </div>
  )
}

export default App
