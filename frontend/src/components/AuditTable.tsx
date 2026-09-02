import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import './AuditTable.css';

interface AuditTrailEntry {
  worker_name: string;
  rank_at_offer: number;
  dispatch_score: number;
  status: string;
  created_at: string;
}

interface AuditTableProps {
  bookingId: string;
}

export function AuditTable({ bookingId }: AuditTableProps) {
  const {
    data: auditTrail,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['auditTrail', bookingId],
    queryFn: async () => {
      const response = await api.get(`/booking-offers/booking/${bookingId}`);
      return response as AuditTrailEntry[];
    },
  });

  if (isLoading) return <div className="p-4 text-center">Loading audit trail...</div>;
  if (isError || !auditTrail)
    return <div className="p-4 text-center text-status-error">Failed to load audit trail</div>;

  return (
    <div className="audit-table-container">
      <table className="audit-table">
        <thead>
          <tr>
            <th>Worker Name</th>
            <th>Rank</th>
            <th>Dispatch Score</th>
            <th>Status</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {auditTrail.map((entry, idx) => (
            <tr key={idx}>
              <td>{entry.worker_name}</td>
              <td>#{entry.rank_at_offer}</td>
              <td className="font-mono">{entry.dispatch_score}</td>
              <td>
                <span className={`status-badge status-${entry.status}`}>{entry.status}</span>
              </td>
              <td>{new Date(entry.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
