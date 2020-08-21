import React, { useState, useEffect } from 'react'
import { useRouteMatch, Link } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Skeleton from 'react-loading-skeleton'

import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'

import { getTask } from 'services/tasks'

import Submission from '../submissions/submit-dialog'

const TaskView = () => {
  const [task, setTask] = useState(null)
  const [error, setError] = useState(null)
  const isAdmin = useSelector(state => state.auth.isAdmin)

  const match = useRouteMatch('/task/:taskId')
  const taskId = match?.params.taskId

  useEffect(() => {
    setError(null)
    setTask(null)

    if (taskId) {
      getTask(taskId)
        .then(task => setTask(task))
        .catch(response => {
          setTask(null)
          setError(response)
        })
    } else {
      setError({ statusText: 'Task not specified' })
    }
  }, [taskId])

  return (() => {
    if (task == null && error == null) {
      return (
        <>
          <Skeleton count='1' height='2rem' className='my-3' />
          <Skeleton count='15' />
        </>
      )
    } else if (error != null) {
      const { status, statusText } = error
      return (
        <>
          {status && (<h3>{status}</h3>)}
          {statusText && (<p>{statusText}</p>)}
        </>
      )
    } else {
      return (
        <Container>
          <Row className='my-1'>
            <Col>
              <h2>
                {task.name}
              </h2>
              {isAdmin && (<small className='text-muted'>Task id {taskId}</small>)}
            </Col>
          </Row>
          <Row className='my-1'>
            <Col>
              <p>{task.description}</p>
            </Col>
          </Row>
          <Row className='my-1 mb-5'>
            <Col>
              <Button as={Link} to={'/submission/' + taskId}>Submissions</Button>
            </Col>
          </Row>
          <Row className='my-1'>
            <Col>
              <p>
                Place your solution here and hit submit.
              </p>
              <Submission taskId={taskId} />
            </Col>
          </Row>
        </Container>
      )
    }
  })()
}

export default TaskView
