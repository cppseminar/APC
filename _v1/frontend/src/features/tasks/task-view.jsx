import React, { useState, useEffect } from 'react'
import { useRouteMatch, Link } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Skeleton from 'react-loading-skeleton'

import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'

import { isAdmin } from '../../app/selectors'
import { getTask } from 'services/tasks'
import DownloadSubmissions from '../download-submissions'
import Submission from '../submissions/submit-dialog'

const TaskView = () => {
  const [task, setTask] = useState(null)
  const [error, setError] = useState(null)
  const admin = useSelector(isAdmin)

  const match = useRouteMatch('/task/:taskId')
  const taskId = match?.params.taskId

  useEffect(() => {
    setError(null)
    setTask(null)

    if (taskId) {
      getTask(taskId)
        .then(task => {
          setTask(task)
          setError(null)
        })
        .catch(error => {
          console.log('Error ', error)
          setTask(null)
          setError(error)
        })
    } else {
      setError({ statusText: 'Task not specified, please select one.' })
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
              {admin && <DownloadSubmissions taskId={taskId} />}
            </Col>
          </Row>
          <Row className='my-1'>
            <Col>
              <p>{task.description}</p>
            </Col>
          </Row>
          <Row className='my-1 mb-5'>
            <Col>
              <Button as={Link} to={'/submission/' + taskId}>View submissions</Button>
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
