import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Register } from './pages/Register';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { WorkerDashboard } from './pages/WorkerDashboard';
import { Book } from './pages/Book';
import { BookingStatus } from './pages/BookingStatus';

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
          <Route path="/worker/dashboard" element={<WorkerDashboard />} />
          {/* Add placeholders for other worker tabs to prevent 404s when navigating */}
          <Route path="/worker/offers" element={<WorkerDashboard />} />
          <Route path="/worker/wallet" element={<WorkerDashboard />} />
          <Route path="/worker/profile" element={<WorkerDashboard />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
