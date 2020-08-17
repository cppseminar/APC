import React, { useState, useEffect } from 'react'
import { UserManager, Log } from 'oidc-client'

import { useDispatch, useSelector } from 'react-redux'

import { setUser, removeUser } from '../../services/auth'

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

const Button = () => {
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

    um.events.addUserUnloaded(dispatch(removeUser))

    um.signinSilent().catch(dispatch(removeUser))
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

  const firstLogin = (<button onClick={login}>Login</button>)
  const loggedOn = (
    <>
      <button onClick={switchUser}>Switch user</button>
      {img ? <img alt='avatar' src={img} /> : ''}{name + ' (' + email + ')'}
      <h5>Your Access Token:</h5>
      <textarea readOnly value={token} />
    </>
  )

  return (
    <div>
      {!token ? firstLogin : loggedOn}
    </div>
  )
}

export const CallbackPage = () => {
  useEffect(() => {
    new UserManager().signinCallback(window.location.href)
  })

  return null
}

export default Button
