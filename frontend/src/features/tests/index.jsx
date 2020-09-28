import React, { useState, useCallback, useEffect } from 'react'
import { submitTest } from 'services/testCases'

import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Alert from 'react-bootstrap/Alert'
import { useParams } from 'react-router-dom'

import TestList from './tests'
import TestCases from './testCases'

const Tests = ({ taskId }) => {
  const [hidden, setHidden] = useState(false)
  const [retCode, setCode] = useState(null)
  const [refresh, setRefresh] = useState(0)
  const { submissionId } = useParams()

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
  const memoizedCb = useCallback((caseId) => {
    setHidden(true)
    const f = (caseId) => {
      submitTest(caseId, submissionId).then(result => {
        setHidden(false)
        setCode(Number(result.status))
        setRefresh(refresh + 1)
      }).catch(error => {
        setHidden(false)
        if (error.response.status) {
          setCode(error.response.status)
        } else {
          setCode(500)
        }
      })
    }
    f(caseId)
  }, [submissionId, refresh])

  if (hidden) {
    return null
  }

  return (
    <Container>
      <Row>
        <Col>
          <TestList submissionId={submissionId} refresh={refresh} />
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
