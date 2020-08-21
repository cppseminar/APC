import React from 'react'
import CardDeck from 'react-bootstrap/CardDeck'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'
import { Link } from 'react-router-dom'

const LandingPage = () => {
  return (
    <CardDeck className='mt-5'>
      <Card>
        <Card.Img variant='top' src='holder.js/100px160' />
        <Card.Body>
          <Card.Title>Tasks</Card.Title>
          <Card.Text>
            Your assigment tasks for every week. There you can also send
            submissions and run tests. Although much of that is not working...
          </Card.Text>
          <Button as={Link} to='/task' size='lg' block>Tasks</Button>
        </Card.Body>
        <Card.Footer>
          <small className='text-muted'>Last updated 3 mins ago</small>
        </Card.Footer>
      </Card>
      <Card>
        <Card.Img variant='top' src='holder.js/100px160' />
        <Card.Body>
          <Card.Title>Card title</Card.Title>
          <Card.Text>
            This card has supporting text below as a natural lead-in to additional
            content.{' '}
          </Card.Text>
        </Card.Body>
        <Card.Footer>
          <small className='text-muted'>Last updated 3 mins ago</small>
        </Card.Footer>
      </Card>
      <Card>
        <Card.Img variant='top' src='holder.js/100px160' />
        <Card.Body>
          <Card.Title>Card title</Card.Title>
          <Card.Text>
            This is a wider card with supporting text below as a natural lead-in to
            additional content. This card has even longer content than the first to
            show that equal height action.
          </Card.Text>
        </Card.Body>
        <Card.Footer>
          <small className='text-muted'>Last updated 3 mins ago</small>
        </Card.Footer>
      </Card>
    </CardDeck>
  )
}

export default LandingPage
