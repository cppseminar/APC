import React, { useState, useEffect } from 'react'
import {
  NavLink,
  useRouteMatch
} from 'react-router-dom'

import { getTasks } from 'services/tasks'
import { useSelector } from 'react-redux'
import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import ListGroup from 'react-bootstrap/ListGroup'

import TaskView from './task-view'

const Tasks = () => {
  const [tasks, setTasks] = useState([])

  const data = useRouteMatch()

  const user = useSelector(state => state.auth.token)

  const refreshTasks = () => {
    getTasks()
      .then((response) => setTasks(response))
      .catch(() => setTasks(null))
  }

  useEffect(() => {
    refreshTasks()
  }, [user])

  return (
    <div>
      <h1>All your tasks</h1>
      <Container>
        <Row>
          <Col sm={3}>
            <ListGroup>
              {tasks.map(val => (
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
      <Button onClick={refreshTasks}>Refresh</Button>
    </div>
  )
}

export default Tasks
