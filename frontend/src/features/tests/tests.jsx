import React, { useState, useEffect } from 'react'
import styled from 'styled-components'
import { listTests, getTest } from 'services/testCases'
import ListGroup from 'react-bootstrap/ListGroup'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Button from 'react-bootstrap/Button'

const Result = styled.pre`
  padding: 0.3em;
  color: white;
  background: #2A363B;
`

const Status = Object.freeze({
  INIT: 0,
  LOADING: 1,
  LOADED: 2,
})

const TestRun = (props) => {
  const { caseName, taskName, user, requested, id } = props.data
  const [detailState, setDetailState] = useState(Status.INIT)
  const [detail, setDetail] = useState(null)

  const showDetails = () => {
    setDetailState(Status.LOADING)
    getTest(id).then(data => {
      setDetail(data.description)
      setDetailState(Status.LOADED)
    })
  }

  const buttons = {
    [Status.INIT]: <Button onClick={showDetails}>Show details</Button>,
    [Status.LOADING]: <Button disabled>Loading ... </Button>,
    [Status.LOADED]: <Button onClick={showDetails}>Refresh</Button>,
  }

  // Formatting of test run results
  let details = (
    <Row>
      <Col>
        <Result>
          {detail}
        </Result>
      </Col>
    </Row>)

  if (!detail) {
    details = null
  }

  return (
    <>
      <Row>
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
          <p>{buttons[detailState]}</p>
        </Col>
      </Row>
      {details}
    </>
  )
}

const TestList = ({ submissionId, refresh, taskId, user }) => {
  const [testRuns, setRuns] = useState([])

  useEffect(() => {
    listTests({ submissionId, taskId, user })
      .then(result => setRuns(result))
      .catch(error => console.error(error)) // TODO: Better error handling
  }, [submissionId, refresh, taskId, user])


  console.log(testRuns)
  if (!testRuns.length) {
    return null
  }
  return (
    <>
      <h3>Your recent test runs</h3>
      <ListGroup>
        {testRuns.map(run => (
          <ListGroup.Item as="div" key={run.id}>
            <TestRun data={run} />
          </ListGroup.Item>)
        )}
      </ListGroup>
    </>
  )
}

export default TestList
