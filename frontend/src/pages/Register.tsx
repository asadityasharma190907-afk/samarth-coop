import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useRegisterMutation } from '../hooks/useAuth';
import { RoleCard } from '../components/RoleCard';
import { SkillChips } from '../components/SkillChips';
import { LocationInput } from '../components/LocationInput';
import { VerifiedBadge } from '../components/VerifiedBadge';
import { api } from '../lib/api';
import { CheckCircle2, ShieldCheck, CreditCard, ArrowRight, ArrowLeft } from 'lucide-react';

export function Register() {
  const navigate = useNavigate();
  const registerMutation = useRegisterMutation();

  const [role, setRole] = useState<'citizen' | 'worker'>('citizen');
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);

  // Step 1: Basic Info
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [skill, setSkill] = useState('electrician');
  const [lat, setLat] = useState<number>(26.928);
  const [lng, setLng] = useState<number>(75.81);

  // Step 2: Extended Profile
  const [fatherName, setFatherName] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('1992-05-15');
  const [domicile, setDomicile] = useState('Rajasthan');
  const [localAddress, setLocalAddress] = useState('123 Pink City, Jaipur');
  const [maritalStatus, setMaritalStatus] = useState<'single' | 'married'>('married');
  const [experienceYears, setExperienceYears] = useState<number>(5);
  const [languagesSpoken, setLanguagesSpoken] = useState('Hindi, English');
  const [aadhaarNumber, setAadhaarNumber] = useState('123456789012');

  // Step 3: Aadhaar OTP State
  const [otpSent, setOtpSent] = useState(false);
  const [otpTxId, setOtpTxId] = useState('');
  const [otpInput, setOtpInput] = useState('123456');
  const [aadhaarVerified, setAadhaarVerified] = useState(false);
  const [aadhaarLoading, setAadhaarLoading] = useState(false);
  const [aadhaarError, setAadhaarError] = useState('');

  // Step 4: Razorpay Payment State
  const [paymentOrder, setPaymentOrder] = useState<{ order_id: string; amount: number } | null>(
    null,
  );
  const [paymentCompleted, setPaymentCompleted] = useState(false);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [paymentError, setPaymentError] = useState('');

  // Form Step Validation
  const validateStep1 = () => {
    if (!name.trim()) return 'Name is required';
    if (phone.length < 10) return 'Valid 10-digit phone number is required';
    if (password.length < 6) return 'Password must be at least 6 characters';
    return null;
  };

  const validateStep2 = () => {
    if (!fatherName.trim()) return "Father's name is required";
    if (aadhaarNumber.length !== 12 || !/^\d+$/.test(aadhaarNumber)) {
      return 'Valid 12-digit numeric Aadhaar number is required';
    }
    return null;
  };

  // Step 3: Send & Verify Aadhaar OTP
  const handleSendOtp = async () => {
    setAadhaarLoading(true);
    setAadhaarError('');
    try {
      const res = await api.post('/kyc/aadhaar/send-otp', { aadhaar_number: aadhaarNumber });
      setOtpSent(true);
      setOtpTxId(res.transaction_id || 'tx_simulated');
    } catch (err: any) {
      setAadhaarError(err.message || 'Failed to send OTP');
    } finally {
      setAadhaarLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    setAadhaarLoading(true);
    setAadhaarError('');
    try {
      // In simulation mode, accept 6-digit OTP
      if (otpInput.length !== 6) {
        throw new Error('OTP must be 6 digits');
      }
      setAadhaarVerified(true);
    } catch (err: any) {
      setAadhaarError(err.message || 'OTP Verification failed');
    } finally {
      setAadhaarLoading(false);
    }
  };

  // Step 4: Payment Simulation
  const handleCreatePaymentOrder = async () => {
    setPaymentLoading(true);
    setPaymentError('');
    try {
      const res = await api.post('/kyc/payment/create-order', {});
      setPaymentOrder(res);
    } catch {
      // Offline / Client side mock fallback
      setPaymentOrder({ order_id: `order_test_${Date.now()}`, amount: 50000 });
    } finally {
      setPaymentLoading(false);
    }
  };

  const handleVerifyPayment = async () => {
    setPaymentLoading(true);
    setPaymentError('');
    try {
      setPaymentCompleted(true);
    } catch (err: any) {
      setPaymentError(err.message || 'Payment failed');
    } finally {
      setPaymentLoading(false);
    }
  };

  // Final Registration Submission
  const handleFinalWorkerSubmit = () => {
    const payload: any = {
      role: 'worker',
      name,
      phone,
      password,
      skill,
      lat,
      lng,
      father_name: fatherName,
      date_of_birth: dateOfBirth,
      domicile,
      local_address: localAddress,
      marital_status: maritalStatus,
      experience_years: Number(experienceYears),
      languages_spoken: languagesSpoken,
      aadhaar_number: aadhaarNumber,
    };

    registerMutation.mutate(payload, {
      onSuccess: (data) => {
        localStorage.setItem('samarth_token', data.access_token);
        navigate('/worker/dashboard');
      },
    });
  };

  const handleCitizenSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = { role: 'citizen', name, phone, password };
    registerMutation.mutate(payload, {
      onSuccess: (data) => {
        localStorage.setItem('samarth_token', data.access_token);
        navigate('/dashboard');
      },
    });
  };

  return (
    <div
      style={{
        maxWidth: role === 'worker' ? '540px' : '420px',
        margin: '0 auto',
        padding: 'var(--spacing-xl) var(--spacing-md)',
        transition: 'max-width 0.3s ease',
      }}
    >
      <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-xl)' }}>
        <h1 style={{ fontSize: 'var(--font-size-h2)', marginBottom: 'var(--spacing-xs)' }}>
          Join Samarth
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>
          {role === 'worker'
            ? 'Complete multi-step onboarding & verification'
            : 'Create your account to get started'}
        </p>
      </div>

      <div style={{ display: 'flex', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-lg)' }}>
        <RoleCard
          role="citizen"
          title="Citizen"
          description="Book services"
          selected={role === 'citizen'}
          onClick={() => {
            setRole('citizen');
            setStep(1);
          }}
        />
        <RoleCard
          role="worker"
          title="Worker"
          description="Offer services"
          selected={role === 'worker'}
          onClick={() => {
            setRole('worker');
            setStep(1);
          }}
        />
      </div>

      {/* Worker 4-Step Stepper Header */}
      {role === 'worker' && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: 'var(--spacing-xl)',
            padding: 'var(--spacing-sm)',
            backgroundColor: 'var(--color-surface-card)',
            borderRadius: 'var(--rounded-lg)',
            border: '1px solid var(--color-border-default)',
          }}
        >
          {[
            { num: 1, label: 'Basic' },
            { num: 2, label: 'Profile' },
            { num: 3, label: 'Aadhaar' },
            { num: 4, label: 'Payment' },
          ].map((s) => (
            <div
              key={s.num}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color:
                  step === s.num
                    ? 'var(--color-brand-primary)'
                    : step > s.num
                      ? 'var(--color-status-success)'
                      : 'var(--color-text-muted)',
                fontWeight: step === s.num ? 600 : 500,
                fontSize: 'var(--font-size-caption)',
              }}
            >
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  backgroundColor:
                    step === s.num
                      ? 'var(--color-brand-primary)'
                      : step > s.num
                        ? 'var(--color-status-success)'
                        : 'var(--color-border-default)',
                  color: step >= s.num ? '#fff' : 'var(--color-text-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px',
                }}
              >
                {step > s.num ? '✓' : s.num}
              </div>
              <span>{s.label}</span>
            </div>
          ))}
        </div>
      )}

      {/* Citizen 1-Step Form */}
      {role === 'citizen' ? (
        <form
          onSubmit={handleCitizenSubmit}
          style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
            <label style={{ fontSize: 'var(--font-size-body-sm)', fontWeight: 500 }}>
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="e.g. Ravi Sharma"
              style={{
                padding: '12px',
                border: '1px solid var(--color-border-default)',
                borderRadius: 'var(--rounded-md)',
                fontSize: 'var(--font-size-body)',
              }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
            <label style={{ fontSize: 'var(--font-size-body-sm)', fontWeight: 500 }}>
              Phone Number
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
              minLength={10}
              maxLength={15}
              placeholder="e.g. 9876543210"
              style={{
                padding: '12px',
                border: '1px solid var(--color-border-default)',
                borderRadius: 'var(--rounded-md)',
                fontSize: 'var(--font-size-body)',
              }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
            <label style={{ fontSize: 'var(--font-size-body-sm)', fontWeight: 500 }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              placeholder="••••••••"
              style={{
                padding: '12px',
                border: '1px solid var(--color-border-default)',
                borderRadius: 'var(--rounded-md)',
                fontSize: 'var(--font-size-body)',
              }}
            />
          </div>

          {registerMutation.isError && (
            <div
              style={{ color: 'var(--color-status-error)', fontSize: 'var(--font-size-body-sm)' }}
            >
              {registerMutation.error instanceof Error
                ? registerMutation.error.message
                : 'Registration failed.'}
            </div>
          )}

          <button
            type="submit"
            disabled={registerMutation.isPending}
            style={{
              marginTop: 'var(--spacing-sm)',
              padding: '12px',
              backgroundColor: 'var(--button-primary-bg)',
              color: 'var(--button-primary-text)',
              border: 'none',
              borderRadius: 'var(--button-primary-radius)',
              fontSize: 'var(--font-size-body)',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            {registerMutation.isPending ? 'Registering...' : 'Register'}
          </button>
        </form>
      ) : (
        /* Worker Multi-Step Wizard */
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          {/* Step 1: Basic Info */}
          {step === 1 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                <label style={{ fontSize: 'var(--font-size-body-sm)', fontWeight: 500 }}>
                  Full Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Suresh Kumar"
                  style={{
                    padding: '12px',
                    border: '1px solid var(--color-border-default)',
                    borderRadius: 'var(--rounded-md)',
                  }}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                <label style={{ fontSize: 'var(--font-size-body-sm)', fontWeight: 500 }}>
                  Phone Number
                </label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  maxLength={15}
                  placeholder="e.g. 9111111111"
                  style={{
                    padding: '12px',
                    border: '1px solid var(--color-border-default)',
                    borderRadius: 'var(--rounded-md)',
                  }}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                <label style={{ fontSize: 'var(--font-size-body-sm)', fontWeight: 500 }}>
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  style={{
                    padding: '12px',
                    border: '1px solid var(--color-border-default)',
                    borderRadius: 'var(--rounded-md)',
                  }}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                <label style={{ fontSize: 'var(--font-size-body-sm)', fontWeight: 500 }}>
                  Primary Skill
                </label>
                <SkillChips selectedSkill={skill} onChange={setSkill} />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                <label style={{ fontSize: 'var(--font-size-body-sm)', fontWeight: 500 }}>
                  Service Location
                </label>
                <LocationInput
                  lat={lat}
                  lng={lng}
                  onChange={(newLat, newLng) => {
                    setLat(newLat);
                    setLng(newLng);
                  }}
                />
              </div>

              <button
                type="button"
                onClick={() => {
                  const err = validateStep1();
                  if (err) alert(err);
                  else setStep(2);
                }}
                style={{
                  marginTop: 'var(--spacing-sm)',
                  padding: '12px',
                  backgroundColor: 'var(--button-primary-bg)',
                  color: 'var(--color-text-on-brand)',
                  border: 'none',
                  borderRadius: 'var(--button-primary-radius)',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  cursor: 'pointer',
                }}
              >
                Next: Profile Details <ArrowRight size={18} />
              </button>
            </div>
          )}

          {/* Step 2: Extended KYC Profile */}
          {step === 2 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 'var(--spacing-sm)',
                }}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                  <label style={{ fontSize: 'var(--font-size-caption)', fontWeight: 500 }}>
                    Father's Name
                  </label>
                  <input
                    type="text"
                    value={fatherName}
                    onChange={(e) => setFatherName(e.target.value)}
                    placeholder="e.g. Ramesh Kumar"
                    style={{
                      padding: '10px',
                      border: '1px solid var(--color-border-default)',
                      borderRadius: 'var(--rounded-md)',
                    }}
                  />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                  <label style={{ fontSize: 'var(--font-size-caption)', fontWeight: 500 }}>
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    value={dateOfBirth}
                    onChange={(e) => setDateOfBirth(e.target.value)}
                    style={{
                      padding: '10px',
                      border: '1px solid var(--color-border-default)',
                      borderRadius: 'var(--rounded-md)',
                    }}
                  />
                </div>
              </div>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 'var(--spacing-sm)',
                }}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                  <label style={{ fontSize: 'var(--font-size-caption)', fontWeight: 500 }}>
                    Domicile State
                  </label>
                  <input
                    type="text"
                    value={domicile}
                    onChange={(e) => setDomicile(e.target.value)}
                    placeholder="e.g. Rajasthan"
                    style={{
                      padding: '10px',
                      border: '1px solid var(--color-border-default)',
                      borderRadius: 'var(--rounded-md)',
                    }}
                  />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                  <label style={{ fontSize: 'var(--font-size-caption)', fontWeight: 500 }}>
                    Marital Status
                  </label>
                  <select
                    value={maritalStatus}
                    onChange={(e) => setMaritalStatus(e.target.value as any)}
                    style={{
                      padding: '10px',
                      border: '1px solid var(--color-border-default)',
                      borderRadius: 'var(--rounded-md)',
                    }}
                  >
                    <option value="single">Single</option>
                    <option value="married">Married</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                <label style={{ fontSize: 'var(--font-size-caption)', fontWeight: 500 }}>
                  Local Address
                </label>
                <input
                  type="text"
                  value={localAddress}
                  onChange={(e) => setLocalAddress(e.target.value)}
                  placeholder="e.g. 123 Pink City, Jaipur"
                  style={{
                    padding: '10px',
                    border: '1px solid var(--color-border-default)',
                    borderRadius: 'var(--rounded-md)',
                  }}
                />
              </div>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 'var(--spacing-sm)',
                }}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                  <label style={{ fontSize: 'var(--font-size-caption)', fontWeight: 500 }}>
                    Experience (Years)
                  </label>
                  <input
                    type="number"
                    value={experienceYears}
                    onChange={(e) => setExperienceYears(Number(e.target.value))}
                    min={0}
                    max={50}
                    style={{
                      padding: '10px',
                      border: '1px solid var(--color-border-default)',
                      borderRadius: 'var(--rounded-md)',
                    }}
                  />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                  <label style={{ fontSize: 'var(--font-size-caption)', fontWeight: 500 }}>
                    Languages Spoken
                  </label>
                  <input
                    type="text"
                    value={languagesSpoken}
                    onChange={(e) => setLanguagesSpoken(e.target.value)}
                    placeholder="e.g. Hindi, English"
                    style={{
                      padding: '10px',
                      border: '1px solid var(--color-border-default)',
                      borderRadius: 'var(--rounded-md)',
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                <label style={{ fontSize: 'var(--font-size-caption)', fontWeight: 500 }}>
                  12-Digit Aadhaar Number
                </label>
                <input
                  type="text"
                  value={aadhaarNumber}
                  onChange={(e) => setAadhaarNumber(e.target.value)}
                  maxLength={12}
                  placeholder="123456789012"
                  style={{
                    padding: '10px',
                    border: '1px solid var(--color-border-default)',
                    borderRadius: 'var(--rounded-md)',
                  }}
                />
              </div>

              <div
                style={{
                  display: 'flex',
                  gap: 'var(--spacing-sm)',
                  marginTop: 'var(--spacing-sm)',
                }}
              >
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: 'transparent',
                    border: '1px solid var(--color-border-default)',
                    borderRadius: 'var(--rounded-md)',
                    fontWeight: 500,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                  }}
                >
                  <ArrowLeft size={16} /> Back
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const err = validateStep2();
                    if (err) alert(err);
                    else setStep(3);
                  }}
                  style={{
                    flex: 2,
                    padding: '12px',
                    backgroundColor: 'var(--button-primary-bg)',
                    color: 'var(--color-text-on-brand)',
                    border: 'none',
                    borderRadius: 'var(--rounded-md)',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                  }}
                >
                  Next: Aadhaar Verification <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Aadhaar Verification Simulation */}
          {step === 3 && (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--spacing-md)',
                padding: 'var(--spacing-md)',
                backgroundColor: 'var(--color-surface-card)',
                borderRadius: 'var(--rounded-lg)',
                border: '1px solid var(--color-border-default)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShieldCheck color="var(--color-brand-primary)" size={24} />
                <div>
                  <h3 style={{ margin: 0, fontSize: 'var(--font-size-h4)' }}>
                    Aadhaar Verification
                  </h3>
                  <p
                    style={{
                      margin: 0,
                      fontSize: 'var(--font-size-caption)',
                      color: 'var(--color-text-secondary)',
                    }}
                  >
                    Simulate OTP verification for Aadhaar #{aadhaarNumber}
                  </p>
                </div>
              </div>

              {!aadhaarVerified ? (
                <>
                  {!otpSent ? (
                    <button
                      type="button"
                      onClick={handleSendOtp}
                      disabled={aadhaarLoading}
                      style={{
                        padding: '12px',
                        backgroundColor: 'var(--color-brand-primary)',
                        color: 'var(--color-text-on-brand)',
                        border: 'none',
                        borderRadius: 'var(--rounded-md)',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      {aadhaarLoading ? 'Sending OTP...' : 'Send Aadhaar OTP'}
                    </button>
                  ) : (
                    <div
                      style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}
                    >
                      <div
                        style={{
                          fontSize: 'var(--font-size-caption)',
                          color: 'var(--color-status-success)',
                        }}
                      >
                        OTP sent to Aadhaar linked mobile (Tx: {otpTxId})
                      </div>
                      <input
                        type="text"
                        value={otpInput}
                        onChange={(e) => setOtpInput(e.target.value)}
                        maxLength={6}
                        placeholder="Enter 6-digit OTP"
                        style={{
                          padding: '10px',
                          border: '1px solid var(--color-border-default)',
                          borderRadius: 'var(--rounded-md)',
                        }}
                      />
                      <button
                        type="button"
                        onClick={handleVerifyOtp}
                        disabled={aadhaarLoading}
                        style={{
                          padding: '12px',
                          backgroundColor: 'var(--color-brand-primary)',
                          color: 'var(--color-text-on-brand)',
                          border: 'none',
                          borderRadius: 'var(--rounded-md)',
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}
                      >
                        {aadhaarLoading ? 'Verifying...' : 'Verify OTP'}
                      </button>
                    </div>
                  )}

                  {aadhaarError && (
                    <div
                      style={{
                        color: 'var(--color-status-error)',
                        fontSize: 'var(--font-size-caption)',
                      }}
                    >
                      {aadhaarError}
                    </div>
                  )}
                </>
              ) : (
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '12px 0',
                  }}
                >
                  <CheckCircle2 color="var(--color-status-success)" size={40} />
                  <div style={{ fontWeight: 600, color: 'var(--color-status-success)' }}>
                    Aadhaar OTP Verified Successfully!
                  </div>
                  <VerifiedBadge status="verified" type="police" />
                </div>
              )}

              <div
                style={{
                  display: 'flex',
                  gap: 'var(--spacing-sm)',
                  marginTop: 'var(--spacing-sm)',
                }}
              >
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: 'transparent',
                    border: '1px solid var(--color-border-default)',
                    borderRadius: 'var(--rounded-md)',
                    cursor: 'pointer',
                  }}
                >
                  Back
                </button>
                <button
                  type="button"
                  disabled={!aadhaarVerified}
                  onClick={() => setStep(4)}
                  style={{
                    flex: 2,
                    padding: '12px',
                    backgroundColor: aadhaarVerified
                      ? 'var(--button-primary-bg)'
                      : 'var(--color-border-default)',
                    color: 'var(--color-text-on-brand)',
                    border: 'none',
                    borderRadius: 'var(--rounded-md)',
                    fontWeight: 600,
                    cursor: aadhaarVerified ? 'pointer' : 'not-allowed',
                  }}
                >
                  Next: KYC Payment{' '}
                  <ArrowRight size={16} style={{ display: 'inline', marginLeft: 4 }} />
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Razorpay Payment Simulation */}
          {step === 4 && (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--spacing-md)',
                padding: 'var(--spacing-md)',
                backgroundColor: 'var(--color-surface-card)',
                borderRadius: 'var(--rounded-lg)',
                border: '1px solid var(--color-border-default)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CreditCard color="var(--color-brand-primary)" size={24} />
                <div>
                  <h3 style={{ margin: 0, fontSize: 'var(--font-size-h4)' }}>
                    KYC Verification Fee
                  </h3>
                  <p
                    style={{
                      margin: 0,
                      fontSize: 'var(--font-size-caption)',
                      color: 'var(--color-text-secondary)',
                    }}
                  >
                    Itemized onboarding background check fee
                  </p>
                </div>
              </div>

              <div
                style={{
                  padding: 'var(--spacing-md)',
                  backgroundColor: 'var(--color-surface-bg)',
                  borderRadius: 'var(--rounded-md)',
                  fontSize: 'var(--font-size-body-sm)',
                }}
              >
                <div
                  style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}
                >
                  <span>Police Verification & Aadhaar Fee:</span>
                  <span>₹450.00</span>
                </div>
                <div
                  style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}
                >
                  <span>Cooperative Platform Processing:</span>
                  <span>₹50.00</span>
                </div>
                <hr style={{ borderColor: 'var(--color-border-subtle)', margin: '8px 0' }} />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700 }}>
                  <span>Total Amount Payable:</span>
                  <span>₹500.00</span>
                </div>
              </div>

              {!paymentCompleted ? (
                <>
                  {!paymentOrder ? (
                    <button
                      type="button"
                      onClick={handleCreatePaymentOrder}
                      disabled={paymentLoading}
                      style={{
                        padding: '12px',
                        backgroundColor: 'var(--color-brand-primary)',
                        color: 'var(--color-text-on-brand)',
                        border: 'none',
                        borderRadius: 'var(--rounded-md)',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      {paymentLoading ? 'Generating Order...' : 'Pay ₹500 via Razorpay (Test Mode)'}
                    </button>
                  ) : (
                    <div
                      style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}
                    >
                      <div
                        style={{
                          fontSize: 'var(--font-size-caption)',
                          color: 'var(--color-text-secondary)',
                        }}
                      >
                        Razorpay Order #{paymentOrder.order_id} Generated
                      </div>
                      <button
                        type="button"
                        onClick={handleVerifyPayment}
                        disabled={paymentLoading}
                        style={{
                          padding: '12px',
                          backgroundColor: 'var(--color-status-success)',
                          color: 'var(--color-text-on-brand)',
                          border: 'none',
                          borderRadius: 'var(--rounded-md)',
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}
                      >
                        {paymentLoading ? 'Verifying Payment...' : 'Simulate Payment Success'}
                      </button>
                    </div>
                  )}

                  {paymentError && (
                    <div
                      style={{
                        color: 'var(--color-status-error)',
                        fontSize: 'var(--font-size-caption)',
                      }}
                    >
                      {paymentError}
                    </div>
                  )}
                </>
              ) : (
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '12px 0',
                  }}
                >
                  <CheckCircle2 color="var(--color-status-success)" size={40} />
                  <div style={{ fontWeight: 600, color: 'var(--color-status-success)' }}>
                    Payment Verified & Onboarding Complete!
                  </div>
                </div>
              )}

              <div
                style={{
                  display: 'flex',
                  gap: 'var(--spacing-sm)',
                  marginTop: 'var(--spacing-sm)',
                }}
              >
                <button
                  type="button"
                  onClick={() => setStep(3)}
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: 'transparent',
                    border: '1px solid var(--color-border-default)',
                    borderRadius: 'var(--rounded-md)',
                    cursor: 'pointer',
                  }}
                >
                  Back
                </button>
                <button
                  type="button"
                  disabled={!paymentCompleted || registerMutation.isPending}
                  onClick={handleFinalWorkerSubmit}
                  style={{
                    flex: 2,
                    padding: '12px',
                    backgroundColor: paymentCompleted
                      ? 'var(--button-primary-bg)'
                      : 'var(--color-border-default)',
                    color: 'var(--color-text-on-brand)',
                    border: 'none',
                    borderRadius: 'var(--rounded-md)',
                    fontWeight: 600,
                    cursor: paymentCompleted ? 'pointer' : 'not-allowed',
                  }}
                >
                  {registerMutation.isPending
                    ? 'Registering Worker...'
                    : 'Complete Signup & Go to Dashboard'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      <div style={{ textAlign: 'center', marginTop: 'var(--spacing-lg)' }}>
        <p style={{ fontSize: 'var(--font-size-body-sm)', color: 'var(--color-text-secondary)' }}>
          Already have an account?{' '}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              navigate('/login');
            }}
            style={{
              color: 'var(--color-brand-primary)',
              textDecoration: 'none',
              fontWeight: 500,
            }}
          >
            Log in
          </a>
        </p>
      </div>
    </div>
  );
}
