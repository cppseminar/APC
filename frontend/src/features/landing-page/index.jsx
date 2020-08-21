import React from 'react'
import CardDeck from 'react-bootstrap/CardDeck'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'
import { Link } from 'react-router-dom'

import Standard from '../../assets/jpg/frederick-tubiermont-fJSRg-r7LuI-unsplash.jpg'
import Lecture from '../../assets/jpg/miguel-henriques-RfiBK6Y_upQ-unsplash.jpg'
import Work from '../../assets/jpg/clark-young-fQxMGkYXqFU-unsplash.jpg'

const LandingPage = () => {
  return (
    <CardDeck className='mt-5'>
      <Card>
        <Card.Img variant='top' src={Work} />
        <Card.Body>
          <Card.Title>Tasks</Card.Title>
          <Card.Text>
            Your assigment tasks for every week. There you can also send
            submissions and run tests. Although much of that is not working...
          </Card.Text>
        </Card.Body>
        <Card.Footer>
          <Button as={Link} to='/task' size='lg' block>Tasks</Button>
        </Card.Footer>
      </Card>
      <Card>
        <Card.Img variant='top' src={Lecture} />
        <Card.Body>
          <Card.Title>Course page</Card.Title>
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
