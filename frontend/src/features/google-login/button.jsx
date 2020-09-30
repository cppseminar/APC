import React, { useEffect } from 'react'
import { Button } from 'react-bootstrap'

import { useSelector } from 'react-redux'

import { silentLogin, switchUser, login } from '../../app/auth'

const GoogleLogin = () => {
  const { token, email, name, img } = useSelector(state => {
    return state.auth
  })

  useEffect(() => {
    silentLogin()
  }, [])

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
    </div>
  )
}

export default GoogleLogin
