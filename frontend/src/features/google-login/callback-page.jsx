import { useEffect } from 'react'

import um from '../../app/auth'

const CallbackPage = () => {
  useEffect(() => {
    um.signinCallback(window.location.href)
  })

  return null
}

export default CallbackPage