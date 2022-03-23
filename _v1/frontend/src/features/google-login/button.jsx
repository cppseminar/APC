import React, { useEffect } from 'react'
import { Button } from 'react-bootstrap'

import { useSelector } from 'react-redux'

import { gapiInit, gapiSignIn, gapiSwitchUser } from '../../app/auth'

const GoogleLogin = () => {
  const { token, email, name, img } = useSelector(state => {
    return state.auth
  })

  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://apis.google.com/js/platform.js'
    script.id = 'googleAuth';

    document.head.appendChild(script);
    script.onload = gapiInit
  }, [])

  const firstLogin = (<Button onClick={gapiSignIn}>Login</Button>)
  const loggedOn = (
    <>
      {name + ' (' + email + ') '}
      {img ? <img height='30px' alt='avatar' src={img} /> : ''}{' '}
      <Button size='sm' onClick={gapiSwitchUser}>Switch user</Button>
    </>
  )

  return (
    <div>
      {!token ? firstLogin : loggedOn}
    </div>
  )
}

export default GoogleLogin
