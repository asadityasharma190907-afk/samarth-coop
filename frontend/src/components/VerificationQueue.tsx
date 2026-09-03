import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import './VerificationQueue.css';

interface AdminWorker {
  worker_id: string;
  user_id: string;
  name: string;
  phone: string;
  skill: string;
  verification_status: 'pending' | 'verified' | 'rejected';
  created_at: string;
}

export function VerificationQueue() {
  const queryClient = useQueryClient();
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const { data: workers, isLoading } = useQuery({
    queryKey: ['adminPendingWorkers'],
    queryFn: async () => {
      const response = await api.get('/admin/workers?status=pending');
      return response as AdminWorker[];
    },
  });

  const verifyMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: 'verified' | 'rejected' }) => {
      return api.patch(`/admin/workers/${id}/verify`, { verification_status: status });
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['adminPendingWorkers'] });
      setToast({
        message: `Worker successfully ${variables.status}.`,
        type: 'success',
      });
      setTimeout(() => setToast(null), 3000);
    },
    onError: (error: any) => {
      setToast({
        message: error.message || 'Failed to update worker status.',
        type: 'error',
      });
      setTimeout(() => setToast(null), 3000);
    },
  });

  if (isLoading) {
    return <div className="loading-state">Loading pending verifications...</div>;
  }

  return (
    <div className="verification-queue">
      <h3>Pending Verifications</h3>
      
      {toast && (
        <div className={`toast toast-${toast.type}`} style={{
          padding: '12px 24px', 
          margin: '16px', 
          borderRadius: '4px',
          backgroundColor: toast.type === 'success' ? 'var(--color-success-light)' : 'var(--color-danger-light)',
          color: toast.type === 'success' ? 'var(--color-success-dark)' : 'var(--color-danger-dark)',
          border: `1px solid ${toast.type === 'success' ? 'var(--color-success-main)' : 'var(--color-danger-main)'}`
        }}>
          {toast.message}
        </div>
      )}

      {workers && workers.length > 0 ? (
        <div className="queue-table-container">
          <table className="queue-table">
            <thead>
              <tr>
                <th>Worker Name</th>
                <th>Skill</th>
                <th>Phone</th>
                <th>Registered Date</th>
                <th style={{ textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {workers.map((worker) => (
                <tr key={worker.worker_id}>
                  <td><strong>{worker.name}</strong></td>
                  <td><span className="skill-chip">{worker.skill}</span></td>
                  <td>{worker.phone}</td>
                  <td>{new Date(worker.created_at).toLocaleDateString()}</td>
                  <td className="actions">
                    <button
                      className="btn-reject"
                      onClick={() => verifyMutation.mutate({ id: worker.worker_id, status: 'rejected' })}
                      disabled={verifyMutation.isPending}
                    >
                      Reject
                    </button>
                    <button
                      className="btn-approve"
                      onClick={() => verifyMutation.mutate({ id: worker.worker_id, status: 'verified' })}
                      disabled={verifyMutation.isPending}
                    >
                      {verifyMutation.isPending && verifyMutation.variables?.id === worker.worker_id && verifyMutation.variables?.status === 'verified' 
                        ? 'Approving...' 
                        : 'Approve'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-queue-state">
          No pending worker verifications. All workers are up to date.
        </div>
      )}
    </div>
  );
}
