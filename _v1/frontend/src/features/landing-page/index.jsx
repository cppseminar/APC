import React from 'react'
import CardDeck from 'react-bootstrap/CardDeck'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'
import { Link } from 'react-router-dom'

import { isLoggedIn } from '../../app/selectors'

import Standard from '../../assets/jpg/frederick-tubiermont-fJSRg-r7LuI-unsplash.jpg'
import Lecture from '../../assets/jpg/miguel-henriques-RfiBK6Y_upQ-unsplash.jpg'
import Work from '../../assets/jpg/clark-young-fQxMGkYXqFU-unsplash.jpg'
import { useSelector } from 'react-redux'

const LandingPage = () => {
  const loggedIn = useSelector(isLoggedIn)

  return (
    <CardDeck className='mt-5'>
      <Card>
        <Card.Img variant='top' src={Work} />
        <Card.Body>
          <Card.Title>Assignments</Card.Title>
          <Card.Text>
            All your assignments are here, you can submit your solution and run some basic tests.
          </Card.Text>
        </Card.Body>
        <Card.Footer>
          <Button as={loggedIn ? Link : null} to='/task' size='lg' disabled={!loggedIn} block>Assignments</Button>
        </Card.Footer>
      </Card>
      <Card>
        <Card.Img variant='top' src={Lecture} />
        <Card.Body>
          <Card.Title>Lecture page</Card.Title>
          <Card.Text>
            Contains information, lecture slides and other materials. Complete
            task descriotion with comments and deadlines can also be found here.
          </Card.Text>
        </Card.Body>
        <Card.Footer>
          <Button href='https://cppseminar.eset.sk' size='lg' block>Lecture page</Button>
        </Card.Footer>
      </Card>
      <Card>
        <Card.Img variant='top' src={Standard} />
        <Card.Body>
          <Card.Title>Standard</Card.Title>
          <Card.Text>
            C++ page without direct link to current working draft will be incomplete.
          </Card.Text>
          <Card.Text>
            <a href='https://isocpp.org/files/papers/N4860.pdf'>Pdf version</a>
          </Card.Text>
        </Card.Body>
        <Card.Footer>
          <Button href='https://eel.is/c++draft/' size='lg' block>ISO standard</Button>
        </Card.Footer>
      </Card>
    </CardDeck>
  )
}

export default LandingPage
