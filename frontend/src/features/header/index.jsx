import React from 'react'
import { Navbar } from 'react-bootstrap'
import { Link } from 'react-router-dom'

import GoogleLogin from '../google-login/button'
import UserSelector from '../user-selector'

const Header = () => {
  return (
    <Navbar bg='dark' variant='dark'>
      <Navbar.Brand as={Link} to='/'>
        APC
      </Navbar.Brand>
      <Navbar.Collapse className='justify-content-end'>
        <Navbar.Text>
          <UserSelector />
        </Navbar.Text>
      </Navbar.Collapse>
      <Navbar.Collapse className='justify-content-end'>
        <Navbar.Text>
          <GoogleLogin />
        </Navbar.Text>
      </Navbar.Collapse>
    </Navbar>
  )
}

export default Header
