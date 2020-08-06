import React from 'react';
import {useState} from 'react';
import logo from './logo.svg';
import { Counter } from './features/counter/Counter';
import './App.css';




const Submissions = (props) => {

  let [token, setToken] = useState("")
  let [url, setUrl] = useState("/api/submissions/")
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


const responseGoogleFail = (response) => {
  console.log("Failed")
  console.log(response);
}

// This is from module react-google-login. And it worked fine, but in the evening
// it just stopped, due to CORS on some api it was loading... ¯\_(ツ)_/¯

// const Button = (success, error) => {
//   return <GoogleLogin
//   clientId="576929321854-j4sla3jtq4mlig7n7r0m9h2dl19s1ua5.apps.googleusercontent.com"
//   buttonText="Login with google"
//   onSuccess={success}
//   onFailure={error}
//   cookiePolicy={'single_host_origin'} />
// }

function App() {

  let [message, setMessage] = useState("Hi please sign in")
  let [token, setToken] = useState("")

  const success_callback = (obj) => {
    setMessage("Successful login")
    console.log(obj)
    setToken(obj)
  }


  const fail = () => {
    setMessage("Failed login")
  }


  const googleClick = () => {
    window.gapi.auth2.authorize({
      client_id: '576929321854-j4sla3jtq4mlig7n7r0m9h2dl19s1ua5.apps.googleusercontent.com',
      scope: 'email profile openid',
      response_type: 'id_token permission'
    }, function(response) {
      if (response.error) {
        fail()
        return;
      }
      // The user authorized the application for the scopes requested.
      var accessToken = response.access_token;
      success_callback(response.id_token)
      // You can also now use gapi.client to perform authenticated requests.
    });
    
  }


  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <Counter />
        {/* <Button success={success_callback} error={responseGoogleFail}/> */}
        <button onClick={googleClick}>Login google</button>
        

        <p>
          {message}
        </p>
        <hr style={{width: "10em"}}/>
        <p>
          Google token: 
        </p>

        <textarea value={token}/>

        <Submissions/>
      

      
      </header>
    </div>
  );
}

export default App;
