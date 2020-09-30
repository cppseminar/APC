import axios from 'axios'

import store from './store'

const api = axios.create({
  baseURL: process.env.REACT_APP_API_DOMAIN,
  timeout: 60000,
  params: {},
  headers: {}
})

const changeAuthentication = () => {
  const auth = store.getState().auth
  if (auth) {
    api.defaults.headers.common.Authorization = 'Bearer ' + auth.token
    if (process.env.NODE_ENV === 'development') {
      // api.defaults.headers.common['X-REQUEST-EMAIL'] = auth.email
    }
  }
}

store.subscribe(changeAuthentication)

changeAuthentication() // load it for the first time

export default api
