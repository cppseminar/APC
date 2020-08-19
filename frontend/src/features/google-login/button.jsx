import React, { useState, useEffect } from 'react'
import { Button } from 'react-bootstrap'
import { UserManager, Log } from 'oidc-client'

import { useDispatch, useSelector } from 'react-redux'

import {
  BrowserRouter as Router,
  Switch,
  Route
} from 'react-router-dom'

import { setUser, removeUser, firstSilentLoginFinished } from '../../services/auth'

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

export const CallbackPage = () => {
  useEffect(() => {
    new UserManager().signinCallback(window.location.href)
  })

  return null
}

const GoogleLogin = () => {
  const [um] = useState(new UserManager(config))
  const dispatch = useDispatch()

  const { token, email, name, img } = useSelector(state => {
    return state.auth
  })

  useEffect(() => {
    um.events.addUserLoaded((user) => {
      const payload = {
        token: user.id_token,
        name: user.profile.name ?? '',
        email: user.profile.email ?? '',
        img: user.profile.picture ?? ''
      }
      dispatch(setUser(payload))
    })

    um.events.addUserUnloaded(() => { dispatch(removeUser()) })

    um.signinSilent()
      .catch(() => { dispatch(removeUser()) })
      .finally(() => { dispatch(firstSilentLoginFinished()) })
  }, [um, dispatch])

  const login = () => {
    um.signinPopup().catch((reason) => {
      console.log('Failed to log in! ' + reason)
    })
  }

  const switchUser = () => {
    um.signinPopup({ prompt: 'select_account' }).catch((reason) => {
      console.log('Failed to switch user! ' + reason)
    })
  }

  const firstLogin = (<Button onClick={login}>Login</Button>)
  const loggedOn = (
    <>
      {name + ' (' + email + ') '}
      {img ? <img height='30px' alt='avatar' src={img} /> : ''}{' '}
      <Button size='sm' onClick={switchUser}>Switch user</Button>
    </>
  )

  return (
    <div>
      {!token ? firstLogin : loggedOn}
      <Router>
        <Switch>
          <Route path='/.auth/google/login'>
            <CallbackPage />
          </Route>
        </Switch>
      </Router>
    </div>
  )
}

export default GoogleLogin
