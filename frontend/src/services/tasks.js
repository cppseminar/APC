import {selectToken} from 'services/auth'

import store from 'app/store';




export const getHeaders = () => {
  const token = selectToken(store.getState())
  const headers = {
    "Authorization": "Bearer " + token,
  }
  if (process.env.NODE_ENV === 'development') {
    headers["X-REQUEST-EMAIL"] = "miro@example.com"
  }
  return headers
}

const verifyResponse = (response) => {
  if (!response.ok) {
    console.log(response)
    throw Error("Badddddd :( "    )
  }
  return response.json()
}

const catchError = (response) => {
  console.log(response)
  alert("You have new error in console")
}

export const getTasks = async () => {
  return fetch( process.env.REACT_APP_API_DOMAIN + "/api/tasks", {
    "headers": getHeaders()
  }).then(verifyResponse).catch(catchError)
}


export const getTask = async (taskId) => {
  return fetch( process.env.REACT_APP_API_DOMAIN + "/api/tasks/" + taskId, {
    "headers": getHeaders()
  }).then(verifyResponse).catch(catchError)
}
