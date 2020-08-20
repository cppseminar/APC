import React from 'react'
import { useSelector } from 'react-redux'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  Redirect,
  useLocation
} from 'react-router-dom'

import Header from './features/header'

import Tasks from './features/tasks'
import Submissions from './features/submissions'

if (process.env.NODE_ENV === 'development') {
  console.log('Current environment ', process.env)
}

const Body = () => {
  const { pathname } = useLocation()

  return (
    <Switch>
      <Redirect from='/:url*(/+)' to={pathname.slice(0, -1)} />
      <Route path='/task'>
        <Tasks />
      </Route>
      <Route path='/submission/:taskId'>
        <Submissions />
      </Route>
      <Route path='/'>
        <h3><Link to='/task'>Tasks</Link></h3>
      </Route>
    </Switch>
  )
}

const App = () => {
  const loading = useSelector(state => state.auth.firstSilentLoginRunning)

  const body = loading ? null : (<Body />)

  return (
    <Router>
      <Header />
      <Container>
        <Row>
          <Col>
            {body}
          </Col>
        </Row>
      </Container>
    </Router>
  )
}

export default App
