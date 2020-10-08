import React, { useEffect } from 'react'
import Form from 'react-bootstrap/Form'
import { useSelector, useDispatch } from 'react-redux'

import { getAdmin, getStudents } from '../../app/selectors'
import { setUsers, selectUser } from '../../app/reducers/users'

import { getUsers } from '../../services/users'

const UserSelector = () => {
  const admin = useSelector(getAdmin)
  const dispatch = useDispatch()
  const students = useSelector(getStudents)

  useEffect(() => {
    if (admin) {
      getUsers()
        .then(data => dispatch(setUsers(data)))
        .catch(error => {
          console.log(error)
          dispatch(setUsers([]))
        })
    }
  }, [admin, dispatch])

  if (!admin) {
    return null
  }

  const onChange = (e) => {
    dispatch(selectUser(e.target.value))
  }

  return (
    <>
      <span>Admin mode</span>{' '}
      <Form inline className='d-inline'>
        <Form.Label className='d-inline' htmlFor='user-select-dropdown'>
          User:{' '}
        </Form.Label>
        <Form.Control id='user-select-dropdown' size='sm' as='select' onChange={onChange}>
          <option value=''>Default</option>
          {students.map(x => ( <option key={x}>{x}</option> ))}
        </Form.Control>
      </Form>
    </>
  )
}

export default UserSelector
