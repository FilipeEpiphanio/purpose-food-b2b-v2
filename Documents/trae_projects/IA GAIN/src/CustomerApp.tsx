import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import CustomerLayout from './components/ui/CustomerLayout';
import CustomerHome from './pages/customer/CustomerHome';
import CustomerProducts from './pages/customer/CustomerProducts';
import ShoppingCart from './pages/customer/ShoppingCart';
import Checkout from './pages/customer/Checkout';
import CustomerLogin from './pages/customer/CustomerLogin';
import CustomerOrders from './pages/customer/CustomerOrders';
import { useCustomerStore } from './store/customerStore';

// Componente para proteger rotas que requerem autenticação
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { customer } = useCustomerStore();
  
  if (!customer) {
    return <Navigate to="/customer/login" replace />;
  }
  
  return <>{children}</>;
};

const CustomerApp: React.FC = () => {
  return (
    <Router basename="/customer">
      <Routes>
        {/* Rotas públicas */}
        <Route path="/login" element={<CustomerLogin />} />
        
        {/* Rotas com layout do cliente */}
        <Route path="/" element={<CustomerLayout children={undefined} />}>
          <Route index element={<CustomerHome />} />
          <Route path="products" element={<CustomerProducts />} />
          <Route path="cart" element={<ShoppingCart />} />
          
          {/* Rotas protegidas */}
          <Route path="checkout" element={
            <ProtectedRoute>
              <Checkout />
            </ProtectedRoute>
          } />
          <Route path="orders" element={
            <ProtectedRoute>
              <CustomerOrders />
            </ProtectedRoute>
          } />
        </Route>
        
        {/* Redirecionamento padrão */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default CustomerApp;