import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import Layout from '@/components/Layout/Layout';
import Dashboard from '@/pages/Dashboard';
import Products from '@/pages/Products';
import Orders from '@/pages/Orders';
import Customers from '@/pages/Customers';
import Financial from '@/pages/Financial';
import Reports from '@/pages/Reports';
import { Sales } from '@/pages/Sales';
import { SocialMedia } from '@/pages/SocialMedia';
import { Invoices } from '@/pages/Invoices';
import Login from '@/pages/Login';
import Notifications from '@/pages/Notifications';
import Profile from '@/pages/Profile';
import Settings from '@/pages/Settings';
import Calendar from '@/pages/Calendar';
import EventForm from '@/pages/EventForm';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuthStore } from '@/stores/authStore';
import { useActivityMonitor } from '@/hooks/usePreventLogout';

export default function App() {
  const { checkAuth, initializeAuthListener } = useAuthStore();

  // Monitorar atividade do usuário para manter sessão ativa
  useActivityMonitor();

  useEffect(() => {
    checkAuth();
    initializeAuthListener();
  }, [checkAuth, initializeAuthListener]);

  return (
    <Router>
      <Routes>
        {/* Admin Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/" element={
          <ProtectedRoute>
            <Layout><Dashboard /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/produtos" element={
          <ProtectedRoute>
            <Layout><Products /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/pedidos" element={
          <ProtectedRoute>
            <Layout><Orders /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/clientes" element={
          <ProtectedRoute>
            <Layout><Customers /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/financeiro" element={
          <ProtectedRoute>
            <Layout><Financial /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/relatorios" element={
          <ProtectedRoute>
            <Layout><Reports /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/vendas" element={
          <ProtectedRoute>
            <Layout><Sales /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/redes-sociais" element={
          <ProtectedRoute>
            <Layout><SocialMedia /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/notas-fiscais" element={
          <ProtectedRoute>
            <Layout><Invoices /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/notifications" element={
          <ProtectedRoute>
            <Layout><Notifications /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/perfil" element={
          <ProtectedRoute>
            <Layout><Profile /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/configuracoes" element={
          <ProtectedRoute>
            <Layout><Settings /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/calendario" element={
          <ProtectedRoute>
            <Layout><Calendar /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/calendario/novo" element={
          <ProtectedRoute>
            <Layout><EventForm /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/calendario/editar/:id" element={
          <ProtectedRoute>
            <Layout><EventForm /></Layout>
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  );
}