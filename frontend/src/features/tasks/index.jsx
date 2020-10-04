import React, { useState, useEffect, useCallback } from 'react'
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

  const loadTasks = useCallback(() => {
    getTasks()
      .then((response) => {
        setState('loaded')
        setTasks(response)
      })
      .catch(() => setState('error'))
  }, [])

  const refreshTasks = () => {
    setState('reloading')

    loadTasks()
  }

  useEffect(() => {
    loadTasks()
  }, [user, loadTasks])

  const errorMessage = (
    <p>
      Tasks cannot be loaded. There were and error on the server or you are not logged in.
    </p>
  )

  const tasksList = (
    <div style={{ position: 'relative' }}>
      {state === 'reloading' && (<LoadingOverlay />)}
      <Container className='mt-3'>
        <Row>
          <Col sm={3}>
            <ListGroup>
              {(tasks ?? []).map(val => (
                <ListGroup.Item key={val.id} as={NavLink} action to={`${data.path}/${val.id}`}>
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
      case 'error': return errorMessage
      default: return null
    }
  })()

  return (
    <>
      <Jumbotron fluid className='py-3 px-3 my-2'>
        <Container>
          <Row>
            <Col>
              <h1 className='display-3'>Assignments</h1>
              <p>
                All your tasks are listed here.
              </p>
            </Col>
            <Col sm='auto'>
              <Button onClick={refreshTasks} disabled={state !== 'loaded' && state !== 'error'}>
                {state === 'loaded' || state === 'error' ? 'Refresh' : 'Loading...'}
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
