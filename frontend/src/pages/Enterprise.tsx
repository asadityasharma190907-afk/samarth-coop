import React, { useState } from 'react';
import { Download, Trash2, Plus } from 'lucide-react';
import { useCreateBulkBooking } from '../hooks/useEnterprise';
import { SKILL_CATEGORIES } from '../components/SkillCategoryGrid';
import './Enterprise.css';

type Schedule = 'daily' | 'weekly' | 'monthly';

interface ServiceRow {
  skill: string;
  quantity: number;
  schedule: Schedule;
}

export function Enterprise() {
  const [institutionName, setInstitutionName] = useState('');
  const [services, setServices] = useState<ServiceRow[]>([
    { skill: 'electrician', quantity: 1, schedule: 'daily' },
  ]);

  const createBulkBooking = useCreateBulkBooking();

  const handleAddService = () => {
    setServices([...services, { skill: 'electrician', quantity: 1, schedule: 'daily' }]);
  };

  const handleRemoveService = (index: number) => {
    if (services.length > 1) {
      setServices(services.filter((_, i) => i !== index));
    }
  };

  const handleServiceChange = (index: number, field: keyof ServiceRow, value: string | number) => {
    const newServices = [...services];
    newServices[index] = { ...newServices[index], [field]: value } as any;
    setServices(newServices);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!institutionName.trim() || services.length === 0) return;

    createBulkBooking.mutate({
      institution_name: institutionName,
      services,
    });
  };

  const handlePrint = () => {
    window.print();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="enterprise-container">
      <div className="enterprise-header">
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
            placeholder="e.g. District Collectorate Office"
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Required Services</label>

          {services.map((service, index) => (
            <div key={index} className="service-row">
              <div>
                <select
                  className="form-select"
                  value={service.skill}
                  onChange={(e) => handleServiceChange(index, 'skill', e.target.value)}
                >
                  {SKILL_CATEGORIES.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <input
                  type="number"
                  min="1"
                  className="form-input"
                  value={service.quantity}
                  onChange={(e) =>
                    handleServiceChange(index, 'quantity', parseInt(e.target.value) || 1)
                  }
                />
              </div>

              <div>
                <select
                  className="form-select"
                  value={service.schedule}
                  onChange={(e) =>
                    handleServiceChange(index, 'schedule', e.target.value as Schedule)
                  }
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <div>
                <button
                  type="button"
                  className="btn-remove"
                  onClick={() => handleRemoveService(index)}
                  disabled={services.length === 1}
                  aria-label="Remove service"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="form-actions">
          <button type="button" className="btn-add-service" onClick={handleAddService}>
            <Plus
              size={16}
              style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '4px' }}
            />
            Add another service
          </button>

          <button
            type="submit"
            className="btn-primary"
            disabled={createBulkBooking.isPending || !institutionName.trim()}
          >
            {createBulkBooking.isPending ? 'Calculating...' : 'Calculate Estimate'}
          </button>
        </div>
      </form>

      {createBulkBooking.isSuccess && createBulkBooking.data && (
        <div className="result-card">
          <div className="result-header">
            <h2 className="result-title">Contract Estimate Summary</h2>
            <p style={{ color: 'var(--color-text-secondary)', margin: '8px 0 0 0' }}>
              For {institutionName}
            </p>
          </div>

          <div className="result-grid">
            <div className="result-item">
              <span className="result-label">Total Bookings / Month</span>
              <span className="result-value">
                {createBulkBooking.data.total_bookings_per_month}
              </span>
            </div>

            <div className="result-item">
              <span className="result-label">Workers Needed</span>
              <span className="result-value">{createBulkBooking.data.workers_needed}</span>
            </div>

            <div className="result-item">
              <span className="result-label">Estimated Monthly Cost</span>
              <span className="result-value">
                {formatCurrency(createBulkBooking.data.estimated_monthly_cost)}
              </span>
            </div>

            <div className="result-item">
              <span className="result-label">Welfare Fund Contribution</span>
              <span className="result-value welfare">
                {formatCurrency(createBulkBooking.data.welfare_fund_contribution)}
              </span>
            </div>
          </div>

          <button type="button" className="btn-download" onClick={handlePrint}>
            <Download size={20} />
            Download Contract PDF
          </button>
        </div>
      )}
    </div>
  );
}
