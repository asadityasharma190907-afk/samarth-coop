import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Register } from './pages/Register';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { WorkerDashboard } from './pages/WorkerDashboard';
import { WorkerHome } from './pages/WorkerHome';
import { Book } from './pages/Book';
import { BookingStatus } from './pages/BookingStatus';
import { WorkerOffers } from './pages/WorkerOffers';
import { WorkerWallet } from './pages/WorkerWallet';
import { Federation } from './pages/Federation';

import { WorkerProfile } from './pages/WorkerProfile';

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/book" element={<Book />} />
          <Route path="/booking/:id" element={<BookingStatus />} />
          <Route path="/worker" element={<WorkerDashboard />}>
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<WorkerHome />} />
            <Route path="offers" element={<WorkerOffers />} />
            <Route path="wallet" element={<WorkerWallet />} />
            <Route path="profile" element={<WorkerProfile />} />
          </Route>
          <Route path="/federation" element={<Federation />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
