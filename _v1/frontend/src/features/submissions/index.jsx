import React, { useState, useEffect } from 'react'
import { Route, NavLink, useRouteMatch } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Button from 'react-bootstrap/Button'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Badge from 'react-bootstrap/Badge'
import Jumbotron from 'react-bootstrap/Jumbotron'
import ListGroup from 'react-bootstrap/ListGroup'

import { getSubmissions } from '../../services/submissions'
import { getSelectedUser } from '../../app/selectors'

import Submission from './submission'
import Tests from '../tests'

const Submissions = () => {
  const [submissions, setSubmissions] = useState([])

  const match = useRouteMatch()
  const taskId = match?.params.taskId

  const user = useSelector(getSelectedUser)

  const refreshSubmissions = (taskId) => {
    getSubmissions(taskId)
      .then((response) => setSubmissions(response))
      .catch(() => setSubmissions(null))
  }

  useEffect(() => {
    refreshSubmissions(taskId)
  }, [user, taskId])

  const taskName = submissions[0]?.taskName ?? ''

  const getBadge = (value) => {
    if (value.testsRunCount > 0) {
      return ( <Badge variant='info'>TEST</Badge> )
    }

    return null
  }

  const timeFormat = new Intl.DateTimeFormat({}, {
      formatMatcher: "basic",
      hour12: false,
      year: "numeric",
      month:"2-digit",
      day:"2-digit",
      hour:"2-digit",
      minute:"2-digit",
      second:"2-digit",
    }
  )

  const body = (
    <Container>
      <Row>
        <Col sm={3}>
          <ListGroup>
            {submissions.map(val => (
              <ListGroup.Item key={val.id} as={NavLink} to={`${match.url}/${val.id}`} action>
                  { timeFormat.format(new Date(val.date))}
                  &nbsp;
                  &nbsp;
                { getBadge(val) }
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Col>
        <Col sm={9}>
          <Route path={`${match.path}/:submissionId`}>
            <Submission />
            <hr/>
            <Tests taskId={taskId} />
          </Route>
        </Col>
      </Row>
    </Container>
  )

  return (
    <>
      <Jumbotron fluid className='py-3 px-3 my-2'>
        <Container>
          <Row>
            <Col>
              <h1 className='display-3'>Submissions for {taskName}</h1>
              <p>
                All your submissions are listed here.
              </p>
            </Col>
            <Col sm='auto'>
              <Button onClick={() => { refreshSubmissions(taskId) }}>Refresh</Button>
            </Col>
          </Row>
        </Container>
      </Jumbotron>
      {body}
    </>
  )
}

export default Submissions
