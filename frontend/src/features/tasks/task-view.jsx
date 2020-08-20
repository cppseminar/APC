import React, { useState, useEffect } from 'react'
import { useRouteMatch, Link } from 'react-router-dom'
import isEmpty from 'lodash/isEmpty'

import Button from 'react-bootstrap/Button'

import { getTask } from 'services/tasks'

import Submission from '../submissions/submit-dialog'

const TaskView = () => {
  const [task, setTask] = useState({})

  const match = useRouteMatch('/task/:taskId')
  const taskId = match?.params.taskId

  useEffect(() => {
    if (taskId) {
      getTask(taskId).then((task) => setTask(task)).catch(setTask(null))
    }
  }, [taskId])

  return isEmpty(task) ? 'Error!' : (
    <div style={{ border: '1px solid green' }}>
      <p>Showing task id {taskId}</p>
      <h2>
        {task.name}
      </h2>
      <p>
        {task.description}
      </p>
      <Button as={Link} to={'/submission/' + taskId}>Submissions</Button>
      <Submission taskId={taskId} />
    </div>
  )
}

export default TaskView
