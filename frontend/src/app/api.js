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
    // api.defaults.params.user = auth.email
    if (process.env.NODE_ENV === 'development') {
      // api.defaults.headers.common['X-REQUEST-EMAIL'] = auth.email
    }

  }
}

// this is a workaround, because of bug in axios, where default parameters
// are not working, this is a regression in v0.19, once it is fixed, we
// can remove this and use the commented line in changeAuthentication
api.interceptors.request.use(config => {
  config.params = config.params || {}
  config.params.user = store.getState().auth?.email ?? ''
  return config
})

store.subscribe(changeAuthentication)

changeAuthentication() // load it for the first time

export default api
