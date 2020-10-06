import { UserManager, Log } from 'oidc-client'

import store from './store'
import { setUser, removeUser, firstSilentLoginFinished } from './reducers/auth'

if (process.env.NODE_ENV !== 'production') {
  Log.logger = console
  Log.level = Log.INFO
}

const config = {
  authority: 'https://accounts.google.com/',
  client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
  redirect_uri: window.location.protocol + '//' + window.location.host + '/.auth/google/login',
  scope: 'email profile openid',
  automaticSilentRenew: true
}

const um = new UserManager(config)

um.events.addUserLoaded((user) => {
  const payload = {
    token: user.id_token,
    name: user.profile.name ?? '',
    email: user.profile.email ?? '',
    img: user.profile.picture ?? ''
  }

  store.dispatch(setUser(payload))
})

um.events.addUserUnloaded(() => { store.dispatch(removeUser()) })

export function silentLogin() {
  um.signinSilent()
    .catch(() => { store.dispatch(removeUser()) })
    .finally(() => { store.dispatch(firstSilentLoginFinished()) })
}

export function switchUser() {
  um.signinPopup({ prompt: 'select_account' }).catch((reason) => {
    console.log('Failed to switch user! ' + reason)
  })
}

export function login() {
  um.signinPopup().catch((reason) => {
    console.log('Failed to log in! ' + reason)
  })
}

export function refreshToken() {
  return um.signinSilent()
    .catch(() => { store.dispatch(removeUser()) })
}

export default um
