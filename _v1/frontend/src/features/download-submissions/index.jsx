import React, { useCallback } from 'react'
import { Button } from 'react-bootstrap'

import { getDownloadSubmissionsLink } from '../../services/submissions'

const DownloadSubmissions = ({taskId}) => {
  const download = useCallback(() => {
    getDownloadSubmissionsLink(taskId)
      .then((response) => {
        window.location.assign(response.link)
      })
      .catch((error) => {
        console.log(error)
      })
  }, [taskId])

  return (
    <Button onClick={download}>
      Download all students submissions
    </Button>
  )
}

export default DownloadSubmissions
