import store from './store'
import { setUser, removeUser, refreshToken, firstSilentLoginFinished } from './reducers/auth'

function userChangedHandler(user) {
  const profile = user.getBasicProfile()

  console.log(user.getAuthResponse())

  const payload = {
    token: user.getAuthResponse().id_token,
    name: profile.getName() ?? '',
    email: profile.getEmail() ?? '',
    img: profile.getImageUrl() ?? ''
  }

  store.dispatch(setUser(payload))
}

export function gapiSignIn() {
  const instance = window.gapi.auth2.getAuthInstance()

  instance.signIn()
    .then(user => userChangedHandler(user))
    .catch(error => {
      console.log(error.error)
      store.dispatch(removeUser())
    })
}

export function gapiSwitchUser() {
  const instance = window.gapi.auth2.getAuthInstance()

  instance.signIn({
    prompt: 'select_account'
  }).then(user => userChangedHandler(user))
    .catch(error => {
      console.log(error.error)
      if (error.error !== 'popup_closed_by_user') {
        store.dispatch(removeUser())
      }
    })
}

export async function gapiRefreshToken() {
  const instance = window.gapi.auth2.getAuthInstance()

  if (instance.isSignedIn.get()) {
    const user = instance.currentUser.get()
    return user.reloadAuthResponse()
      .then(response => {
        console.log(response)
        store.dispatch(refreshToken(response.id_token))

        return response
      })
      .catch(error => {
        console.log(error.error)
        store.dispatch(removeUser())
      })
  }

  throw new Error('User not signed in.')
}

export function gapiInit() {
  window.gapi.load('auth2', () => {
    window.gapi.auth2.init({
      client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
      scope: 'email profile openid',
      ux_mode: 'popup',
      redirect_uri: window.location.protocol + '//' + window.location.host + '/.auth/google/login',
    }).then((instance) => {
      if (instance.isSignedIn.get()) {
        userChangedHandler(instance.currentUser.get())
      }

      store.dispatch(firstSilentLoginFinished)
    }, (error) => {
      console.error("Initialization of gapi failed", error)
    })
  })
}
