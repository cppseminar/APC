import axios from 'axios'
import createAuthRefreshInterceptor from 'axios-auth-refresh'

import store from './store'
import { gapiRefreshToken } from './auth'

const api = axios.create({
  baseURL: process.env.REACT_APP_API_DOMAIN,
  timeout: 60000,
  params: {},
  headers: {}
})

const refreshAuthLogic = async failedRequest => {
  try {
    const user = await gapiRefreshToken()

    failedRequest.response.config.headers['Authorization'] = 'Bearer ' + user.id_token

    return Promise.resolve()
  } catch (e) {
    return Promise.reject(failedRequest)
  }
}

createAuthRefreshInterceptor(api, refreshAuthLogic, {
  pauseInstanceWhileRefreshing: true,
  statusCodes: [ 401 ]
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
