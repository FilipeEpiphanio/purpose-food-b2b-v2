import React from 'react'
import { Routes, Route } from 'react-router-dom'
import CustomerLayout from '../components/ui/CustomerLayout'
import CustomerHome from '../pages/customer/CustomerHome'
import CustomerProducts from '../pages/customer/CustomerProducts'
import CustomerCart from '../pages/customer/ShoppingCart'
import CustomerCheckout from '../pages/customer/CustomerCheckout'
import CustomerOrders from '../pages/customer/CustomerOrders'

function CustomerApp() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<CustomerLayout><CustomerHome /></CustomerLayout>} />
        <Route path="cardapio" element={<CustomerLayout><CustomerProducts /></CustomerLayout>} />
        <Route path="carrinho" element={<CustomerLayout><CustomerCart /></CustomerLayout>} />
        <Route path="checkout" element={<CustomerLayout><CustomerCheckout /></CustomerLayout>} />
        <Route path="pedidos" element={<CustomerLayout><CustomerOrders /></CustomerLayout>} />
      </Routes>
    </div>
  )
}

export default CustomerApp