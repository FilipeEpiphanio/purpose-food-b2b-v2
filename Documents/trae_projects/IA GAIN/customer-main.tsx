import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import CustomerApp from './customer/CustomerApp.tsx'
import './index.css'

// Criar root para o cliente
const customerRoot = document.getElementById('customer-root')
if (customerRoot) {
  createRoot(customerRoot).render(
    <StrictMode>
      <BrowserRouter>
        <CustomerApp />
      </BrowserRouter>
    </StrictMode>,
  )
}