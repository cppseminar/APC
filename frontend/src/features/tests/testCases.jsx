import React, { useState, useEffect } from 'react'
import { getCases } from 'services/testCases'
import ListGroup from 'react-bootstrap/ListGroup'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Button from 'react-bootstrap/Button'


const TestCase = ({ data, runTestCallback }) => {
  const { name, numRunsAllowed } = data
  const runTest = runTestCallback

  return (<ListGroup.Item as="div">
    <Row>
      <Col>
        {name}
      </Col>
      <Col>
        Runs Allowed - {numRunsAllowed}
      </Col>
      <Col>
        <Button onClick={runTest}>Run test</Button>
      </Col>
    </Row>
  </ListGroup.Item>)
}

const TestCases = ({ taskId, runCaseCallback }) => {
  const [cases, setCases] = useState([])

  // TODO: Add some global error display
  useEffect(() => {
    getCases(taskId)
      .then(result => setCases(result))
  }, [taskId])

  return (
    <ListGroup variant='flush'>
      {cases.map(val => (<TestCase key={val.id} data={val} runTestCallback={() => runCaseCallback(val.id)} />))}
    </ListGroup>
  )
}

export default TestCases
