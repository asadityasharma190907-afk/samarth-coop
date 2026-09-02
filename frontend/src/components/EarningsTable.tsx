import React from 'react';
import { EarningsEntry } from '../hooks/useWallet';
import './EarningsTable.css';

interface EarningsTableProps {
  entries: EarningsEntry[];
}

export function EarningsTable({ entries }: EarningsTableProps) {
  if (!entries || entries.length === 0) {
    return (
      <div className="earnings-empty">
        <p>No completed jobs yet. Accept some offers to start earning!</p>
      </div>
    );
  }

  return (
    <div className="earnings-table-container">
      <table className="earnings-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Service</th>
            <th className="text-right">Job Price</th>
            <th className="text-right">Your Payout</th>
            <th className="text-right welfare-column">Welfare Fund</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => {
            const date = new Date(entry.created_at).toLocaleDateString();
            const jobPrice = Number(entry.job_price);
            const platformFee = Number(entry.platform_fee);
            const payout = jobPrice - platformFee;

            return (
              <tr key={entry.id}>
                <td>{date}</td>
                <td className="capitalize">{entry.skill}</td>
                <td className="text-right font-mono">₹{jobPrice.toFixed(2)}</td>
                <td className="text-right font-mono text-status-success font-medium">
                  ₹{payout.toFixed(2)}
                </td>
                <td className="text-right font-mono text-welfare-fund">
                  ₹{platformFee.toFixed(2)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
