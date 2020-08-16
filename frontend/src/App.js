import React from 'react'
import {useState} from 'react'
import { Counter } from './features/counter/Counter'
import './App.css'

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
} from "react-router-dom"

import GoogleLogin, { CallbackPage } from './features/google-login/button'

import Tasks from './pages/tasks'

if (process.env.NODE_ENV === 'development') {
  console.log('Current environment ', process.env)
}

const Submissions = (props) => {

  let [token, setToken] = useState("")
  let [url, setUrl] = useState((process.env.REACT_APP_API_DOMAIN ?? '') + '/api/submissions/')
  let [response, setResponse] = useState("")
  let [code, setCode] = useState(0)

  let headers = {}
  if (token) {
    headers = {
      "headers" : {
        "Authorization" : "Bearer " + token
      }
    }
  }
  const submit = () =>  {
    fetch(url, headers).then(response => {setCode(response.status)
      return response.json()
    }).then(json => setResponse(JSON.stringify(json, null, 2))).catch( (obj) => {
      setResponse("Some error")
      console.log(obj)
    })
  }

  console.log(token)
  return (
    <>
    <div>
      Set token:
      <input type="text" onChange={(event) => setToken(event.target.value)} value={token} />
      Set url:
      <input type="text" onChange={(event) => setUrl(event.target.value)} value={url} />
    </div>
    <div>
      <button onClick={submit} >Request!</button>
    </div>
    <div style={{border: "1px solid black"}}>
      <p>Response code {code}</p>
      <pre style={{border: "1px solid blue", textAlign: "left"}}>
        {response}
      </pre>
    </div>
    </>
  )
}

const App = () => {
  return (
    <div className="App">
      <Router>
        <Switch>
          <Route path='/.auth/google/login'>
            <CallbackPage />
          </Route>
          <Route path='/task/'>
            <Tasks/>
          </Route>
          <Route path='/'>
            <header className="App-header">
              <h3><Link to="/task" >Tasks</Link></h3>
              <p>But first login!</p>
              <Counter />

              <GoogleLogin />
              <hr style={{width: "10em"}}/>

              <Submissions/>

            </header>
          </Route>

        </Switch>
      </Router>
    </div>
  );
}

export default App;
