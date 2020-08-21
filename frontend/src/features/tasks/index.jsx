import React, { useState, useEffect } from 'react'
import { NavLink, useRouteMatch } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import ListGroup from 'react-bootstrap/ListGroup'
import Jumbotron from 'react-bootstrap/Jumbotron'
import Skeleton from 'react-loading-skeleton'

import { getTasks } from 'services/tasks'

import TaskView from './task-view'
import LoadingOverlay from '../loading-overlay'

const Tasks = () => {
  const [tasks, setTasks] = useState([])
  const [state, setState] = useState('loading')

  const data = useRouteMatch()

  const user = useSelector(state => state.auth.token)

  const refreshTasks = () => {
    state !== 'loading' && setState('reloading') // differentiate between first load and subsequent fetch
    getTasks()
      .then((response) => setTasks(response))
      .catch(() => setTasks(null))
      .finally(() => setState('loaded'))
  }

  useEffect(() => {
    refreshTasks()
  }, [user])

  const tasksList = (
    <div style={{position: 'relative'}}>
      {state === 'reloading' && (<LoadingOverlay />)}
      <Container className='mt-3'>
        <Row>
          <Col sm={3}>
            <ListGroup>
              {(tasks ?? []).map(val => (
                <ListGroup.Item key={val._id} as={NavLink} action to={`${data.path}/${val._id}`}>
                  {val.name}
                </ListGroup.Item>
              ))}
            </ListGroup>
          </Col>
          <Col sm={9}>
            <TaskView />
          </Col>
        </Row>
      </Container>
    </div>
  )

  const skeleton = (
    <Container className='mt-3'>
      <Row>
        <Col sm={3}>
          <Skeleton count='1' height='20rem' />
        </Col>
        <Col sm={9}>
          <Skeleton count='1' height='2rem' className='my-3' />
          <Skeleton count='15' />
        </Col>
      </Row>
    </Container>
  )

  const body = (() => {
    switch (state) {
      case 'loading': return skeleton
      case 'loaded':
      case 'reloading': return tasksList
      default: return null
    }
  })()

  return (
    <>
      <Jumbotron fluid className='py-3 px-3 my-2'>
        <Container>
          <Row>
            <Col>
              <h1 className='display-3'>Tasks</h1>
              <p>
                All your tasks are listed here. 
              </p>
            </Col>
            <Col sm='auto'>
              <Button onClick={refreshTasks} disabled={state !== 'loaded'}>
                {state === 'loaded' ? 'Refresh' : 'Loading...'}
              </Button>
            </Col>
          </Row>
        </Container>
      </Jumbotron>
      {body}
    </>
  )
}

export default Tasks
