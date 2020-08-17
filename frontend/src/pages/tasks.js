import React, { useState, useEffect } from 'react'

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useParams,
  useRouteMatch
} from 'react-router-dom'
import { getTasks, getTask } from 'services/tasks'

const TaskView = () => {
  const taskId = useParams().taskId
  const [task, setTask] = useState({})

  useEffect(() => {
    getTask(taskId).then((task) => setTask(task))
  }, [taskId])

  return (
    <div style={{ border: '1px solid green' }}>
      <p>Showing task id {taskId}</p>
      <h4>
        {task.name}

      </h4>
      <p>

        {task.description}
      </p>

    </div>
  )
}
function cutUrl (url) {
  return url.replace(/\/+$/, '')
}
const Tasks = () => {
  const [tasks, setTasks] = useState([])
  const { url } = useRouteMatch()

  const refreshTasks = () => {
    getTasks().then((response) => setTasks(response))
  }

  return (
    <div>
      <Router>
        <strong>All your tasks (Click refresh)</strong>
        <br />
        <button onClick={refreshTasks}>Refresh</button>

        <ul>
          {tasks.map(val => (
            <li key={val._id}>
              <Link to={`${cutUrl(url)}/${val._id}`}>{val.name}</Link>
            </li>
          ))}
        </ul>
        <Switch>
          <Route path='/task/:taskId'>
            <TaskView />
          </Route>
        </Switch>
      </Router>
    </div>
  )
}

export default Tasks
