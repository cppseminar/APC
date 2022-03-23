import React, { useState, useEffect } from 'react'
import styled from 'styled-components'
import { listTests, getTest } from 'services/testCases'
import ListGroup from 'react-bootstrap/ListGroup'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Button from 'react-bootstrap/Button'
import _ from 'lodash'

const Result = styled.pre`
  padding: 0.3em;
  color: white;
  background: #2A363B;
`

// This is called in _.map and adds returns react objects
const colorizeInternal = (testLine) => {
  testLine = String(testLine)

  if (testLine.indexOf("[OK]") === 0) {
    return <><span style={{color:"lightgreen"}}>[INFO]</span>{testLine.slice(4)}</>
  }
  if (testLine.indexOf("[INFO]") === 0) {
    return <><span style={{color:"lightgreen"}}>[INFO]</span>{testLine.slice(6)}</>
  }
  if (testLine.indexOf("[WARNING]") === 0) {
    return <><span style={{color:"orange"}}>[WARNING]</span>{testLine.slice(9)}</>
  }
  if (testLine.indexOf("[ERROR]") === 0) {
    return <><span style={{color:"red"}}>[ERROR]</span>{testLine.slice(7)}</>
  }
  return <>{testLine}</>
}

const colorizeTestRun = (testRunString) => {
  const plain = String(testRunString)
  const lines = plain.split('\n')
  const appendNewLine = (line, index) => {
    return <span key={index}>{line}{"\n"}</span>
  }
  const colorized =  _.map(lines, colorizeInternal)
  return _.map(colorized, appendNewLine)
}

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
          {colorizeTestRun(detail)}
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
