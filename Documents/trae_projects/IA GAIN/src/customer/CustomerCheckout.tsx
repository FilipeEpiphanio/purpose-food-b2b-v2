import React from 'react'

const CustomerOrders: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Meus Pedidos</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-600">Você ainda não tem pedidos.</p>
      </div>
    </div>
  )
}

export default CustomerOrders