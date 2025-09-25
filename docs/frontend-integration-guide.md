# Frontend Integration Guide

This comprehensive guide covers how to integrate with the Lunaxcode CMS Admin API from your frontend application, with a focus on the onboarding flow system.

## Table of Contents

- [Authentication](#authentication)
- [Base Configuration](#base-configuration)
- [Onboarding System Integration](#onboarding-system-integration)
- [Content Management](#content-management)
- [Error Handling](#error-handling)
- [TypeScript Definitions](#typescript-definitions)
- [React Integration Examples](#react-integration-examples)
- [Best Practices](#best-practices)

## Authentication

### Initial Setup

The API uses Bearer token authentication. First, authenticate to get an access token:

```javascript
// Login to get access token
const login = async (credentials) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: credentials.username,
      password: credentials.password
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Store token securely
    localStorage.setItem('access_token', data.access_token);
    return data;
  }
  
  throw new Error(data.detail || 'Login failed');
};
```

### API Client Setup

Create a base API client with authentication:

```javascript
class ApiClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }
  
  getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
        ...options.headers,
      },
      ...options,
    };
    
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    
    return response.json();
  }
  
  async get(endpoint) {
    return this.request(endpoint);
  }
  
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  
  async patch(endpoint, data) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }
  
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }
}

// Initialize client
const apiClient = new ApiClient('http://localhost:8000');
```

## Base Configuration

### Environment Variables

```javascript
// config.js
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  ENDPOINTS: {
    // Authentication
    LOGIN: '/api/v1/auth/login',
    LOGOUT: '/api/v1/auth/logout',
    VERIFY_TOKEN: '/api/v1/auth/verify-token',
    
    // Onboarding
    ONBOARDING_STEPS: '/api/v1/onboarding/steps',
    ONBOARDING_FLOW_START: '/api/v1/onboarding/flow/start',
    ONBOARDING_FLOW_SUBMIT: '/api/v1/onboarding/flow/submit',
    ONBOARDING_FLOW_STATE: '/api/v1/onboarding/flow',
    ONBOARDING_FLOW_BACK: '/api/v1/onboarding/flow',
    ONBOARDING_FLOW_SKIP: '/api/v1/onboarding/flow',
    
    // Content
    PRICING_PLANS: '/api/v1/pricing-plans',
    FEATURES: '/api/v1/features',
    FAQS: '/api/v1/faqs',
    CONTACT_INFO: '/api/v1/contact-info',
    SITE_SETTINGS: '/api/v1/site-settings',
  }
};
```

## Onboarding System Integration

### Step 1: Initialize Onboarding Flow

```javascript
class OnboardingService {
  constructor(apiClient) {
    this.apiClient = apiClient;
  }
  
  async startFlow(serviceType, deviceInfo = {}) {
    const payload = {
      service_type: serviceType, // 'landing_page', 'web_app', or 'mobile_app'
      user_agent: navigator.userAgent,
      device_type: this.detectDeviceType(),
      screen_resolution: `${screen.width}x${screen.height}`,
      ...deviceInfo
    };
    
    return this.apiClient.post('/api/v1/onboarding/flow/start', payload);
  }
  
  detectDeviceType() {
    const width = window.innerWidth;
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    return 'desktop';
  }
}
```

### Step 2: Handle Step Navigation

```javascript
class OnboardingFlow {
  constructor(apiClient) {
    this.apiClient = apiClient;
    this.sessionId = null;
    this.currentStep = null;
    this.flowConfig = null;
  }
  
  async initialize(serviceType) {
    const response = await this.apiClient.post('/api/v1/onboarding/flow/start', {
      service_type: serviceType,
      user_agent: navigator.userAgent,
      device_type: this.detectDeviceType(),
      screen_resolution: `${screen.width}x${screen.height}`
    });
    
    this.sessionId = response.session_id;
    this.currentStep = response.current_step;
    this.flowConfig = response.flow_config;
    
    return response;
  }
  
  async submitStepData(stepId, formData, timeSpent = null) {
    const payload = {
      session_id: this.sessionId,
      step_id: stepId,
      step_data: formData,
      time_spent: timeSpent,
      device_type: this.detectDeviceType(),
      user_agent: navigator.userAgent
    };
    
    const response = await this.apiClient.post('/api/v1/onboarding/flow/submit', payload);
    
    if (response.success && response.next_step) {
      this.currentStep = response.next_step;
    }
    
    return response;
  }
  
  async goBack() {
    const response = await this.apiClient.post(
      `/api/v1/onboarding/flow/${this.sessionId}/back`
    );
    
    if (response.success && response.previous_step) {
      this.currentStep = response.previous_step;
    }
    
    return response;
  }
  
  async skipStep(stepId) {
    const response = await this.apiClient.post(
      `/api/v1/onboarding/flow/${this.sessionId}/skip`,
      null,
      { params: { step_id: stepId } }
    );
    
    if (response.success && response.next_step) {
      this.currentStep = response.next_step;
    }
    
    return response;
  }
  
  async getFlowState() {
    return this.apiClient.get(`/api/v1/onboarding/flow/${this.sessionId}`);
  }
  
  detectDeviceType() {
    const width = window.innerWidth;
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    return 'desktop';
  }
}
```

### Step 3: Form Validation

```javascript
class OnboardingValidator {
  static validateStep(step, formData) {
    const errors = [];
    const warnings = [];
    
    if (!step.validation_schema) {
      return { is_valid: true, errors, warnings };
    }
    
    // Basic validation based on required fields
    if (step.required_fields) {
      step.required_fields.forEach(field => {
        if (!formData[field] || formData[field].toString().trim() === '') {
          errors.push({
            field,
            message: `${field} is required`,
            code: 'REQUIRED_FIELD'
          });
        }
      });
    }
    
    // Email validation
    if (formData.contactEmail && !this.isValidEmail(formData.contactEmail)) {
      errors.push({
        field: 'contactEmail',
        message: 'Please enter a valid email address',
        code: 'INVALID_EMAIL'
      });
    }
    
    // Project description length
    if (formData.projectDescription && formData.projectDescription.length < 10) {
      errors.push({
        field: 'projectDescription',
        message: 'Project description must be at least 10 characters long',
        code: 'MIN_LENGTH'
      });
    }
    
    return {
      is_valid: errors.length === 0,
      errors,
      warnings
    };
  }
  
  static isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}
```

## Content Management

### Pricing Plans

```javascript
class PricingService {
  constructor(apiClient) {
    this.apiClient = apiClient;
  }
  
  async getAll(filters = {}) {
    const params = new URLSearchParams({
      page: filters.page || 1,
      size: filters.size || 20,
      ...(filters.category && { category: filters.category }),
      ...(filters.active_only !== undefined && { active_only: filters.active_only })
    });
    
    return this.apiClient.get(`/api/v1/pricing-plans/?${params}`);
  }
  
  async getPopular(limit = 3) {
    return this.apiClient.get(`/api/v1/pricing-plans/popular?limit=${limit}`);
  }
  
  async getByCategory(category) {
    return this.apiClient.get(`/api/v1/pricing-plans/category/${category}`);
  }
  
  async create(planData) {
    return this.apiClient.post('/api/v1/pricing-plans/', planData);
  }
  
  async update(id, planData) {
    return this.apiClient.patch(`/api/v1/pricing-plans/${id}`, planData);
  }
  
  async delete(id, hardDelete = false) {
    return this.apiClient.delete(`/api/v1/pricing-plans/${id}?hard_delete=${hardDelete}`);
  }
}
```

### Site Settings

```javascript
class SettingsService {
  constructor(apiClient) {
    this.apiClient = apiClient;
  }
  
  async getPublicSettings() {
    return this.apiClient.get('/api/v1/site-settings/public');
  }
  
  async getSetting(key) {
    return this.apiClient.get(`/api/v1/site-settings/key/${key}`);
  }
  
  async updateSetting(id, value) {
    return this.apiClient.patch(`/api/v1/site-settings/${id}`, { value });
  }
}
```

## Error Handling

### Global Error Handler

```javascript
class ErrorHandler {
  static handle(error, context = '') {
    console.error(`Error in ${context}:`, error);
    
    if (error.message.includes('401')) {
      this.handleAuthError();
      return;
    }
    
    if (error.message.includes('403')) {
      this.showError('You do not have permission to perform this action.');
      return;
    }
    
    if (error.message.includes('404')) {
      this.showError('The requested resource was not found.');
      return;
    }
    
    if (error.message.includes('422')) {
      this.showError('Please check your input and try again.');
      return;
    }
    
    if (error.message.includes('500')) {
      this.showError('A server error occurred. Please try again later.');
      return;
    }
    
    this.showError(error.message || 'An unexpected error occurred.');
  }
  
  static handleAuthError() {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  }
  
  static showError(message) {
    // Implement your preferred error display method
    // Could be a toast, modal, or banner
    console.error('User Error:', message);
  }
}
```

## TypeScript Definitions

```typescript
// types/api.ts

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// Onboarding Types
export interface OnboardingStep {
  id: string;
  created_at: string;
  updated_at: string;
  step_number: number;
  step_name: 'service_selection' | 'basic_info' | 'service_requirements' | 'review' | 'confirmation';
  step_title: string;
  step_description?: string;
  validation_schema?: Record<string, any>;
  required_fields?: string[];
  optional_fields?: string[];
  component_type: 'form' | 'selection' | 'review' | 'confirmation';
  form_config?: Record<string, any>;
  ui_layout: 'single_column' | 'two_column' | 'grid' | 'custom';
  next_step_conditions?: Record<string, any>;
  skip_conditions?: Record<string, any>;
  back_allowed: boolean;
  service_types?: string[];
  is_conditional: boolean;
  conditional_logic?: Record<string, any>;
  display_order: number;
  progress_weight: number;
  estimated_time?: number;
  is_active: boolean;
  is_required: boolean;
}

export interface OnboardingFlowState {
  session_id: string;
  submission_id?: string;
  current_step: number;
  current_step_name: string;
  step_history: string[];
  form_data: Record<string, any>;
  service_type: 'landing_page' | 'web_app' | 'mobile_app';
  is_complete: boolean;
  started_at: string;
  last_active_at: string;
}

export interface StartOnboardingFlowRequest {
  service_type: 'landing_page' | 'web_app' | 'mobile_app';
  user_agent?: string;
  device_type?: 'desktop' | 'tablet' | 'mobile';
  screen_resolution?: string;
}

export interface SubmitStepDataRequest {
  session_id: string;
  step_id: string;
  step_data: Record<string, any>;
  time_spent?: number;
  device_type?: 'desktop' | 'tablet' | 'mobile';
  user_agent?: string;
}

export interface ValidationResult {
  is_valid: boolean;
  errors: Array<{
    field: string;
    message: string;
    code: string;
  }>;
  warnings: Array<{
    field: string;
    message: string;
    code: string;
  }>;
}

// Content Types
export interface PricingPlan {
  id: string;
  created_at: string;
  updated_at: string;
  plan_id: string;
  name: string;
  price: string;
  period?: string;
  description: string;
  features: string[];
  button_text: string;
  button_variant: 'default' | 'outline' | 'ghost';
  popular: boolean;
  timeline: string;
  display_order: number;
  category: 'web' | 'mobile';
  is_active: boolean;
}

export interface SiteSetting {
  id: string;
  created_at: string;
  updated_at: string;
  key: string;
  value: string;
  type: 'text' | 'number' | 'boolean' | 'json';
  description?: string;
  is_public: boolean;
}
```

## React Integration Examples

### Onboarding Flow Component

```tsx
// components/OnboardingFlow.tsx
import React, { useState, useEffect } from 'react';
import { OnboardingFlow, OnboardingValidator } from '../services/onboarding';
import { apiClient } from '../services/api';

interface OnboardingFlowProps {
  serviceType: 'landing_page' | 'web_app' | 'mobile_app';
  onComplete: (data: any) => void;
  onExit: () => void;
}

export const OnboardingFlowComponent: React.FC<OnboardingFlowProps> = ({
  serviceType,
  onComplete,
  onExit
}) => {
  const [flow] = useState(() => new OnboardingFlow(apiClient));
  const [currentStep, setCurrentStep] = useState(null);
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [startTime, setStartTime] = useState(Date.now());

  useEffect(() => {
    initializeFlow();
  }, [serviceType]);

  const initializeFlow = async () => {
    try {
      setIsLoading(true);
      const response = await flow.initialize(serviceType);
      setCurrentStep(response.current_step);
      setStartTime(Date.now());
    } catch (error) {
      console.error('Failed to initialize onboarding flow:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStepSubmit = async (stepData: Record<string, any>) => {
    if (!currentStep) return;

    // Client-side validation
    const validation = OnboardingValidator.validateStep(currentStep, stepData);
    if (!validation.is_valid) {
      setErrors(validation.errors);
      return;
    }

    try {
      setIsLoading(true);
      setErrors([]);
      
      const timeSpent = Math.floor((Date.now() - startTime) / 1000);
      const response = await flow.submitStepData(
        currentStep.id,
        stepData,
        timeSpent
      );

      if (response.success) {
        setFormData(prev => ({ ...prev, ...stepData }));
        
        if (response.next_step) {
          setCurrentStep(response.next_step);
          setStartTime(Date.now());
        } else {
          // Flow completed
          onComplete(formData);
        }
      } else {
        setErrors(response.validation_result.errors);
      }
    } catch (error) {
      console.error('Failed to submit step data:', error);
      setErrors([{ field: 'general', message: 'Failed to submit data. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoBack = async () => {
    try {
      const response = await flow.goBack();
      if (response.success && response.previous_step) {
        setCurrentStep(response.previous_step);
        setStartTime(Date.now());
      }
    } catch (error) {
      console.error('Failed to go back:', error);
    }
  };

  const handleSkip = async () => {
    if (!currentStep || !currentStep.skip_conditions) return;
    
    try {
      const response = await flow.skipStep(currentStep.id);
      if (response.success && response.next_step) {
        setCurrentStep(response.next_step);
        setStartTime(Date.now());
      }
    } catch (error) {
      console.error('Failed to skip step:', error);
    }
  };

  if (isLoading && !currentStep) {
    return <div>Loading onboarding flow...</div>;
  }

  if (!currentStep) {
    return <div>Failed to load onboarding flow.</div>;
  }

  return (
    <div className="onboarding-flow">
      <div className="step-header">
        <h2>{currentStep.step_title}</h2>
        {currentStep.step_description && (
          <p>{currentStep.step_description}</p>
        )}
      </div>

      <StepComponent
        step={currentStep}
        onSubmit={handleStepSubmit}
        onBack={currentStep.back_allowed ? handleGoBack : undefined}
        onSkip={currentStep.skip_conditions ? handleSkip : undefined}
        errors={errors}
        isLoading={isLoading}
        initialData={formData}
      />
    </div>
  );
};
```

### Step Component

```tsx
// components/StepComponent.tsx
import React, { useState } from 'react';
import { OnboardingStep } from '../types/api';

interface StepComponentProps {
  step: OnboardingStep;
  onSubmit: (data: Record<string, any>) => void;
  onBack?: () => void;
  onSkip?: () => void;
  errors: Array<{ field: string; message: string }>;
  isLoading: boolean;
  initialData: Record<string, any>;
}

export const StepComponent: React.FC<StepComponentProps> = ({
  step,
  onSubmit,
  onBack,
  onSkip,
  errors,
  isLoading,
  initialData
}) => {
  const [formData, setFormData] = useState(initialData);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const getFieldError = (fieldName: string) => {
    return errors.find(error => error.field === fieldName)?.message;
  };

  const renderFormField = (field: any) => {
    const error = getFieldError(field.name);
    
    switch (field.type) {
      case 'text':
      case 'email':
      case 'tel':
        return (
          <div key={field.name} className="form-field">
            <label htmlFor={field.name}>{field.label}</label>
            <input
              type={field.type}
              id={field.name}
              name={field.name}
              placeholder={field.placeholder}
              value={formData[field.name] || ''}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                [field.name]: e.target.value
              }))}
              className={error ? 'error' : ''}
            />
            {error && <span className="error-message">{error}</span>}
          </div>
        );
      
      case 'textarea':
        return (
          <div key={field.name} className="form-field">
            <label htmlFor={field.name}>{field.label}</label>
            <textarea
              id={field.name}
              name={field.name}
              placeholder={field.placeholder}
              value={formData[field.name] || ''}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                [field.name]: e.target.value
              }))}
              className={error ? 'error' : ''}
              rows={4}
            />
            {error && <span className="error-message">{error}</span>}
          </div>
        );
      
      case 'select':
        return (
          <div key={field.name} className="form-field">
            <label htmlFor={field.name}>{field.label}</label>
            <select
              id={field.name}
              name={field.name}
              value={formData[field.name] || ''}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                [field.name]: e.target.value
              }))}
              className={error ? 'error' : ''}
            >
              <option value="">Select an option</option>
              {field.options?.map((option: string) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
            {error && <span className="error-message">{error}</span>}
          </div>
        );
      
      default:
        return null;
    }
  };

  // Render based on component type
  switch (step.component_type) {
    case 'selection':
      return (
        <div className="selection-step">
          <div className="options-grid">
            {step.form_config?.options?.map((option: any) => (
              <div
                key={option.value}
                className={`option-card ${formData.serviceType === option.value ? 'selected' : ''}`}
                onClick={() => setFormData({ serviceType: option.value })}
              >
                <h3>{option.label}</h3>
                <p>{option.description}</p>
              </div>
            ))}
          </div>
          
          <div className="step-actions">
            <button
              type="button"
              onClick={() => onSubmit(formData)}
              disabled={!formData.serviceType || isLoading}
            >
              {isLoading ? 'Loading...' : 'Continue'}
            </button>
          </div>
        </div>
      );
    
    case 'form':
      return (
        <form onSubmit={handleSubmit} className="form-step">
          <div className={`form-fields ${step.ui_layout}`}>
            {step.form_config?.fields?.map(renderFormField)}
          </div>
          
          <div className="step-actions">
            {onBack && (
              <button type="button" onClick={onBack} disabled={isLoading}>
                Back
              </button>
            )}
            {onSkip && (
              <button type="button" onClick={onSkip} disabled={isLoading}>
                Skip
              </button>
            )}
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Loading...' : 'Continue'}
            </button>
          </div>
        </form>
      );
    
    case 'review':
      return (
        <div className="review-step">
          <div className="review-sections">
            {/* Render review of collected data */}
            <pre>{JSON.stringify(formData, null, 2)}</pre>
          </div>
          
          <div className="step-actions">
            {onBack && (
              <button type="button" onClick={onBack} disabled={isLoading}>
                Back
              </button>
            )}
            <button
              type="button"
              onClick={() => onSubmit({})}
              disabled={isLoading}
            >
              {isLoading ? 'Submitting...' : 'Submit'}
            </button>
          </div>
        </div>
      );
    
    case 'confirmation':
      return (
        <div className="confirmation-step">
          <div className="confirmation-content">
            <h3>{step.form_config?.message}</h3>
            {step.form_config?.nextSteps && (
              <ul>
                {step.form_config.nextSteps.map((step: string, index: number) => (
                  <li key={index}>{step}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      );
    
    default:
      return <div>Unknown step type</div>;
  }
};
```

## Best Practices

### 1. State Management

```javascript
// Use a state management solution like Redux or Zustand for complex applications
import { create } from 'zustand';

const useOnboardingStore = create((set, get) => ({
  sessionId: null,
  currentStep: null,
  formData: {},
  isLoading: false,
  errors: [],
  
  setSessionId: (sessionId) => set({ sessionId }),
  setCurrentStep: (step) => set({ currentStep: step }),
  updateFormData: (data) => set(state => ({ 
    formData: { ...state.formData, ...data } 
  })),
  setLoading: (loading) => set({ isLoading: loading }),
  setErrors: (errors) => set({ errors }),
  clearErrors: () => set({ errors: [] }),
  
  reset: () => set({
    sessionId: null,
    currentStep: null,
    formData: {},
    isLoading: false,
    errors: []
  })
}));
```

### 2. Caching and Performance

```javascript
// Use React Query or SWR for caching API responses
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useOnboardingSteps = (serviceType) => {
  return useQuery({
    queryKey: ['onboarding-steps', serviceType],
    queryFn: () => apiClient.get(`/api/v1/onboarding/steps?service_type=${serviceType}`),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useStartOnboarding = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data) => apiClient.post('/api/v1/onboarding/flow/start', data),
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries(['onboarding-flow']);
    },
  });
};
```

### 3. Error Boundaries

```tsx
// components/ErrorBoundary.tsx
import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Onboarding error:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong during onboarding</h2>
          <p>Please refresh the page and try again.</p>
          <button onClick={() => window.location.reload()}>
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 4. Analytics Integration

```javascript
// utils/analytics.js
export const trackOnboardingEvent = (eventName, properties = {}) => {
  // Google Analytics
  if (window.gtag) {
    window.gtag('event', eventName, properties);
  }
  
  // Custom analytics
  if (window.analytics) {
    window.analytics.track(eventName, properties);
  }
  
  console.log('Analytics:', eventName, properties);
};

// Usage in onboarding flow
trackOnboardingEvent('onboarding_started', {
  service_type: serviceType,
  device_type: deviceType,
  timestamp: new Date().toISOString()
});

trackOnboardingEvent('onboarding_step_completed', {
  step_name: currentStep.step_name,
  step_number: currentStep.step_number,
  time_spent: timeSpent,
  session_id: sessionId
});
```

### 5. Progressive Enhancement

```javascript
// Check for API availability
const checkApiHealth = async () => {
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
};

// Graceful degradation for offline mode
const useOfflineMode = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  return isOnline;
};
```

## Testing

### API Client Testing

```javascript
// tests/apiClient.test.js
import { describe, it, expect, vi } from 'vitest';
import { ApiClient } from '../services/api';

global.fetch = vi.fn();

describe('ApiClient', () => {
  const apiClient = new ApiClient('http://localhost:8000');
  
  beforeEach(() => {
    fetch.mockClear();
    localStorage.clear();
  });
  
  it('should make authenticated requests', async () => {
    localStorage.setItem('access_token', 'test-token');
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'test' })
    });
    
    await apiClient.get('/test-endpoint');
    
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/test-endpoint',
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': 'Bearer test-token'
        })
      })
    );
  });
});
```

This comprehensive integration guide provides everything needed to integrate with the Lunaxcode CMS Admin API, with particular focus on the onboarding system. The examples are production-ready and include error handling, TypeScript support, and best practices for modern React applications.
