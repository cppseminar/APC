import React, { useState, useEffect } from 'react'
import { listTests } from 'services/testCases'
import ListGroup from 'react-bootstrap/ListGroup'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Button from 'react-bootstrap/Button'


const TestRun = (props) => {
  const { caseName, taskName, user, requested } = props.data
  return (<Row>
    <Col>
      <p>
        <strong>Test run of: </strong>
        {caseName}
      </p>
      <p>
        <small>
          <strong>Task name: </strong>{taskName}
        &nbsp;&nbsp; - &nbsp;&nbsp;
        {new Date(requested).toLocaleString()}
        </small>
      </p>
    </Col>
    <Col>
      <p><em>{user}</em></p>
      <p><Button>Show details</Button></p>
    </Col>
  </Row>)
}

const TestList = ({ submissionId, refresh, taskId }) => {
  const [testRuns, setRuns] = useState([])
  const refreshCb = () => {
    listTests({submissionId, taskId})
      .then(result => setRuns(result))
      .catch(error => console.error(error))
  }
  useEffect(() => refreshCb(), [submissionId, refresh])
  if (!testRuns.length) {
    return null
  }
  return (
    <>
    <h3>Your recent test runs</h3>
    <ListGroup>
      {testRuns.map(run => (
        <ListGroup.Item as="div">
          <TestRun data={run} />
        </ListGroup.Item>)
      )}
    </ListGroup>
    </>
  )
}

export default TestList
