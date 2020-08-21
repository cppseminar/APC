import React from 'react'
import styled from 'styled-components/macro'
import Spinner from 'react-bootstrap/Spinner'

const Overlay = styled.div`
  position: absolute;
  z-index: 11000;
  background-color: rgba(255,255,255,0.8);
  width: 100%;
  height: 100%;
  display: flex;
`

const LoadingOverlay = () => {
  return (
    <Overlay>
      <Spinner animation='border' variant='primary' style={{width: '4rem', height: '4rem', margin: 'auto'}} />
    </Overlay>
  )
}

export default LoadingOverlay
