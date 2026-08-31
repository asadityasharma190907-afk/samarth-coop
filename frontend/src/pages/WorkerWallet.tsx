import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { useWallet } from '../hooks/useWallet';
import { EarningsTable } from '../components/EarningsTable';
import './WorkerWallet.css';

export function WorkerWallet() {
  const { user } = useAuth();
  const { data: wallet, isLoading, isError } = useWallet(user?.id);

  if (!user || user.role !== 'worker') {
    return <div className="p-4 text-center">Unauthorized. Workers only.</div>;
  }

  if (isLoading) {
    return <div className="p-4 text-center">Loading wallet...</div>;
  }

  if (isError || !wallet) {
    return <div className="p-4 text-center text-status-error">Failed to load wallet.</div>;
  }

  const weekly = Number(wallet.weekly_earnings);
  const lifetime = Number(wallet.lifetime_earnings);

  return (
    <div className="wallet-container">
      <header className="wallet-header">
        <h1 className="text-h1 font-bold mb-2">Your Earnings</h1>
        <p className="text-body text-text-secondary mb-6">Track your completed jobs and payouts.</p>
        
        <div className="wallet-cards">
          <div className="wallet-card primary">
            <h3 className="text-body font-medium mb-1">This Week</h3>
            <div className="earnings-amount font-mono">₹{weekly.toFixed(2)}</div>
          </div>
          
          <div className="wallet-card secondary">
            <h3 className="text-body font-medium mb-1">Lifetime Payouts</h3>
            <div className="earnings-amount font-mono">₹{lifetime.toFixed(2)}</div>
          </div>
        </div>
      </header>

      <section className="wallet-history">
        <h2 className="text-h2 font-semibold mb-4">Earning History</h2>
        <EarningsTable entries={wallet.entries} />
      </section>
    </div>
  );
}
