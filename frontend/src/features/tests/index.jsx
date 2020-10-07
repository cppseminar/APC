import React, { useState, useCallback, useEffect } from 'react'
import { useSelector } from 'react-redux'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Alert from 'react-bootstrap/Alert'
import { useParams } from 'react-router-dom'

import TestList from './tests'
import TestCases from './testCases'
import { submitTest } from 'services/testCases'
import { isAdmin, getSelectedUser, getLoggedUser } from '../../app/selectors'

const Tests = ({ taskId }) => {
  const [hidden, setHidden] = useState(false)
  const [retCode, setCode] = useState(null)
  const [refresh, setRefresh] = useState(0)
  const { submissionId } = useParams()

  const user = useSelector(getSelectedUser)

  const admin = useSelector(state => {
    return isAdmin(state) && getSelectedUser(state) !== getLoggedUser(state) ? getLoggedUser(state) : null
  })

  let notification = null

  useEffect(() => {
    setCode(null)
  }, [submissionId])

  if (retCode) {
    notification = <Alert variant="danger ">Unknown error</Alert>
  }
  if (retCode === 201) {
    notification = <Alert variant="success">Submission queued for testing</Alert>
  } else if (retCode === 402) {
    notification = <Alert variant="warning">All test runs are spent</Alert>
  }

  // Network and set return code
  const memoizedCb = useCallback(caseId => {
    setHidden(true)

    submitTest(caseId, submissionId)
      .then(result => {
        setCode(+result.status)
        setRefresh(refresh + 1)
      })
      .catch(error => {
        if (error.response.status) {
          setCode(error.response.status)
        } else {
          setCode(500)
        }
      })
      .finally(() => {
        setHidden(false)
      })
  }, [submissionId, refresh])

  if (hidden) {
    return null
  }

  const adminTestRuns = admin ? (
    <Row>
      <Col>
        <h3>Admin test runs</h3>
        <TestList submissionId={submissionId} refresh={refresh} user={admin} />
      </Col>
    </Row>
  ) : null


  return (
    <Container>
      {adminTestRuns}
      <Row>
        <Col>
          <TestList submissionId={submissionId} refresh={refresh} user={user} />
        </Col>
      </Row>
      <Row>
        <Col>
          {notification}
          <h3>Test cases you can run</h3>
          <TestCases taskId={taskId} runCaseCallback={memoizedCb} />
        </Col>
      </Row>
    </Container>
  )
}

export default Tests
