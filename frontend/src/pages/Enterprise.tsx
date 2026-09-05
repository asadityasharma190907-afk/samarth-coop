import React, { useState } from 'react';
import { Download, Trash2, Plus, Building2, Users, Wallet, CheckCircle2 } from 'lucide-react';
import { useCreateBulkBooking, BulkBookingItem } from '../hooks/useEnterprise';
import { SKILL_CATEGORIES } from '../components/SkillCategoryGrid';
import './Enterprise.css';

type ScheduleType = 'daily' | 'weekly' | 'monthly';

interface ServiceRowState {
  skill: string;
  quantity: number;
  schedule: ScheduleType;
}

export function Enterprise() {
  const [institutionName, setInstitutionName] = useState('');
  const [services, setServices] = useState<ServiceRowState[]>([
    { skill: 'electrician', quantity: 1, schedule: 'daily' },
  ]);

  const createBulkBooking = useCreateBulkBooking();

  const handleAddService = () => {
    setServices((prev) => [...prev, { skill: 'cleaner', quantity: 1, schedule: 'daily' }]);
  };

  const handleRemoveService = (index: number) => {
    if (services.length > 1) {
      setServices((prev) => prev.filter((_, i) => i !== index));
    }
  };

  const handleServiceChange = (
    index: number,
    field: keyof ServiceRowState,
    value: string | number,
  ) => {
    setServices((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], [field]: value } as ServiceRowState;
      return next;
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!institutionName.trim() || services.length === 0) return;

    const payloadBookings: BulkBookingItem[] = services.map((s) => ({
      skill: s.skill,
      quantity: Math.max(1, Number(s.quantity) || 1),
      schedule: s.schedule,
      months: 1,
    }));

    createBulkBooking.mutate({
      institution_name: institutionName.trim(),
      bookings: payloadBookings,
    });
  };

  const handlePrint = () => {
    window.print();
  };

  const formatCurrency = (amount: number | string) => {
    const num = typeof amount === 'string' ? parseFloat(amount) : amount;
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(isNaN(num) ? 0 : num);
  };

  return (
    <div className="enterprise-container">
      <div className="enterprise-header">
        <div className="enterprise-badge">
          <Building2 size={16} />
          <span>Government & Institutional Anchor Portal</span>
        </div>
        <h1 className="enterprise-title">Enterprise / B2G Booking</h1>
        <p className="enterprise-subtitle">Samarth Cooperative Services</p>
      </div>

      <form className="enterprise-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="institutionName">
            Institution Name
          </label>
          <input
            id="institutionName"
            type="text"
            className="form-input"
            value={institutionName}
            onChange={(e) => setInstitutionName(e.target.value)}
            placeholder="e.g. District Collectorate Office, Jaipur"
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Required Services</label>

          {services.map((service, index) => (
            <div key={index} className="service-row" data-testid={`service-row-${index}`}>
              <div className="field-col">
                <label className="sub-label">Skill Category</label>
                <select
                  className="form-select"
                  value={service.skill}
                  aria-label={`Skill category ${index + 1}`}
                  onChange={(e) => handleServiceChange(index, 'skill', e.target.value)}
                >
                  {SKILL_CATEGORIES.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field-col field-qty">
                <label className="sub-label">Quantity</label>
                <input
                  type="number"
                  min="1"
                  className="form-input"
                  aria-label={`Quantity ${index + 1}`}
                  value={service.quantity}
                  onChange={(e) =>
                    handleServiceChange(index, 'quantity', parseInt(e.target.value, 10) || 1)
                  }
                />
              </div>

              <div className="field-col">
                <label className="sub-label">Schedule</label>
                <select
                  className="form-select"
                  value={service.schedule}
                  aria-label={`Schedule ${index + 1}`}
                  onChange={(e) =>
                    handleServiceChange(index, 'schedule', e.target.value as ScheduleType)
                  }
                >
                  <option value="daily">Daily (22 days/mo)</option>
                  <option value="weekly">Weekly (4 days/mo)</option>
                  <option value="monthly">Monthly (1 day/mo)</option>
                </select>
              </div>

              <div className="field-action">
                <button
                  type="button"
                  className="btn-remove"
                  onClick={() => handleRemoveService(index)}
                  disabled={services.length === 1}
                  aria-label={`Remove service ${index + 1}`}
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="form-actions">
          <button type="button" className="btn-add-service" onClick={handleAddService}>
            <Plus size={16} />
            <span>Add another service</span>
          </button>

          <button
            type="submit"
            className="btn-primary"
            disabled={createBulkBooking.isPending || !institutionName.trim()}
          >
            {createBulkBooking.isPending ? 'Calculating...' : 'Calculate Estimate'}
          </button>
        </div>

        {createBulkBooking.isError && (
          <div className="enterprise-error" role="alert">
            {createBulkBooking.error.message || 'Failed to calculate estimate. Please try again.'}
          </div>
        )}
      </form>

      {createBulkBooking.isSuccess && createBulkBooking.data && (
        <div className="result-card" data-testid="result-card">
          <div className="result-header">
            <div className="result-header-title">
              <CheckCircle2 size={24} className="result-success-icon" />
              <h2 className="result-title">Contract Estimate Summary</h2>
            </div>
            <p className="result-institution">
              Prepared for: <strong>{createBulkBooking.data.institution}</strong>
            </p>
            <p className="result-contract-id">
              Contract Ref: <code>{createBulkBooking.data.contract_id}</code>
            </p>
          </div>

          <div className="result-grid">
            <div className="result-item">
              <div className="result-item-icon">
                <Building2 size={20} />
              </div>
              <div>
                <span className="result-label">Total Bookings / Month</span>
                <span className="result-value">{createBulkBooking.data.total_bookings}</span>
              </div>
            </div>

            <div className="result-item">
              <div className="result-item-icon">
                <Users size={20} />
              </div>
              <div>
                <span className="result-label">Cooperative Workers Needed</span>
                <span className="result-value">
                  {createBulkBooking.data.cooperative_workers_needed}
                </span>
              </div>
            </div>

            <div className="result-item">
              <div className="result-item-icon">
                <Wallet size={20} />
              </div>
              <div>
                <span className="result-label">Estimated Monthly Cost</span>
                <span className="result-value">
                  {formatCurrency(createBulkBooking.data.estimated_monthly_cost)}
                </span>
              </div>
            </div>

            <div className="result-item result-item-welfare">
              <div className="result-item-icon welfare-icon">
                <Wallet size={20} />
              </div>
              <div>
                <span className="result-label">Welfare Fund Contribution (5%)</span>
                <span className="result-value welfare">
                  {formatCurrency(createBulkBooking.data.welfare_fund_contribution)}
                </span>
              </div>
            </div>
          </div>

          {createBulkBooking.data.line_items && createBulkBooking.data.line_items.length > 0 && (
            <div className="line-items-section">
              <h3 className="line-items-title">Service Allocation Breakdown</h3>
              <div className="table-responsive">
                <table className="line-items-table">
                  <thead>
                    <tr>
                      <th>Skill</th>
                      <th>Quantity</th>
                      <th>Schedule</th>
                      <th>Monthly Rate</th>
                      <th>Total Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {createBulkBooking.data.line_items.map((item, idx) => (
                      <tr key={idx}>
                        <td className="skill-name">{item.skill}</td>
                        <td>{item.quantity}</td>
                        <td>{item.schedule}</td>
                        <td>{formatCurrency(item.monthly_cost)}</td>
                        <td className="cost-col">{formatCurrency(item.total_cost)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="contract-print-footer">
            <p>Certified by Samarth National Cooperative Federation • Ministry of Cooperation</p>
          </div>

          <button type="button" className="btn-download" onClick={handlePrint}>
            <Download size={20} />
            <span>Download Contract PDF</span>
          </button>
        </div>
      )}
    </div>
  );
}
