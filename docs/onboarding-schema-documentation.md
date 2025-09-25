# Onboarding Steps Process Schema Documentation

## Overview

This document describes the comprehensive schema design for the onboarding steps process in the Lunaxcode.com project. The schema supports a flexible, multi-step onboarding flow with analytics, validation, and service-specific customization.

## 📋 Table of Contents

1. [Database Tables](#database-tables)
2. [TypeScript Types](#typescript-types)
3. [Validation Schemas](#validation-schemas)
4. [Flow Architecture](#flow-architecture)
5. [Implementation Guide](#implementation-guide)
6. [API Endpoints](#api-endpoints)
7. [Analytics & Tracking](#analytics--tracking)

## 🗃️ Database Tables

### 1. onboarding_steps

Defines the configuration for each step in the onboarding process.

| Field | Type | Description |
|-------|------|-------------|
| `id` | text | Unique step identifier |
| `step_number` | integer | Sequential step number |
| `step_name` | text | Step name enum: service_selection, basic_info, service_requirements, review, confirmation |
| `step_title` | text | Display title for the step |
| `step_description` | text | Optional description |
| `validation_schema` | text | JSON validation schema |
| `required_fields` | text | JSON array of required fields |
| `optional_fields` | text | JSON array of optional fields |
| `component_type` | text | UI component type: form, selection, review, confirmation |
| `form_config` | text | JSON form configuration |
| `ui_layout` | text | Layout type: single_column, two_column, grid, custom |
| `next_step_conditions` | text | JSON conditions for next step |
| `skip_conditions` | text | JSON conditions to skip step |
| `back_allowed` | boolean | Whether back navigation is allowed |
| `service_types` | text | JSON array of applicable service types |
| `is_conditional` | boolean | Whether step is conditionally displayed |
| `conditional_logic` | text | JSON conditional logic |
| `display_order` | integer | Display order |
| `progress_weight` | integer | Progress bar weight |
| `estimated_time` | integer | Estimated completion time (minutes) |
| `is_active` | boolean | Whether step is active |
| `is_required` | boolean | Whether step is required |

### 2. onboarding_step_progress

Tracks individual user progress through each step.

| Field | Type | Description |
|-------|------|-------------|
| `id` | text | Unique progress record identifier |
| `submission_id` | text | Reference to onboarding submission |
| `step_id` | text | Reference to onboarding step |
| `step_number` | integer | Step sequence number |
| `step_name` | text | Step name |
| `status` | text | Status: pending, in_progress, completed, skipped, error |
| `step_data` | text | JSON data collected in step |
| `validation_errors` | text | JSON array of validation errors |
| `user_input` | text | JSON raw user input |
| `started_at` | text | When step was started |
| `completed_at` | text | When step was completed |
| `time_spent` | integer | Time spent in seconds |
| `attempt_count` | integer | Number of attempts |
| `previous_step_id` | text | Previous step reference |
| `next_step_id` | text | Next step reference |
| `navigation_history` | text | JSON navigation events |
| `user_agent` | text | User agent string |
| `device_type` | text | Device type: desktop, tablet, mobile |
| `exited_at` | text | If user exited without completing |

### 3. onboarding_analytics

Aggregated analytics and performance data.

| Field | Type | Description |
|-------|------|-------------|
| `id` | text | Unique analytics record identifier |
| `session_id` | text | Session identifier |
| `submission_id` | text | Reference to submission (optional) |
| `total_steps` | integer | Total number of steps |
| `completed_steps` | integer | Number of completed steps |
| `skipped_steps` | integer | Number of skipped steps |
| `error_steps` | integer | Number of steps with errors |
| `total_time_spent` | integer | Total time in seconds |
| `average_step_time` | integer | Average time per step |
| `fastest_step` | text | Fastest completed step |
| `slowest_step` | text | Slowest completed step |
| `completion_rate` | integer | Completion percentage (0-100) |
| `abandoned_at` | text | Step where user abandoned |
| `conversion_status` | text | Status: completed, abandoned, in_progress |
| `back_navigation_count` | integer | Number of back navigations |
| `error_count` | integer | Total error count |
| `retry_count` | integer | Total retry count |
| `help_requested` | boolean | Whether help was requested |
| `performance_score` | integer | Performance score (0-100) |
| `user_experience_score` | integer | UX score (0-100) |
| `technical_issues` | text | JSON array of technical issues |
| `user_agent` | text | User agent string |
| `device_type` | text | Device type |
| `browser_name` | text | Browser name |
| `operating_system` | text | Operating system |
| `screen_resolution` | text | Screen resolution |

## 📝 TypeScript Types

### Core Types

```typescript
export type ServiceType = 'landing_page' | 'web_app' | 'mobile_app';
export type StepName = 'service_selection' | 'basic_info' | 'service_requirements' | 'review' | 'confirmation';
export type StepStatus = 'pending' | 'in_progress' | 'completed' | 'skipped' | 'error';
export type ComponentType = 'form' | 'selection' | 'review' | 'confirmation';
export type UILayout = 'single_column' | 'two_column' | 'grid' | 'custom';
export type DeviceType = 'desktop' | 'tablet' | 'mobile';
export type ConversionStatus = 'completed' | 'abandoned' | 'in_progress';
```

### Configuration Interfaces

```typescript
export interface OnboardingStepConfig {
  id: string;
  stepNumber: number;
  stepName: StepName;
  stepTitle: string;
  stepDescription?: string;
  componentType: ComponentType;
  serviceTypes?: ServiceType[];
  validationSchema?: Record<string, unknown>;
  formConfig?: Record<string, unknown>;
  uiLayout?: UILayout;
  displayOrder: number;
  progressWeight?: number;
  estimatedTime?: number;
  isActive?: boolean;
  isRequired?: boolean;
}
```

### Flow Management

```typescript
export interface OnboardingFlowConfig {
  steps: OnboardingStepConfig[];
  serviceType: ServiceType;
  totalSteps: number;
  currentStep: number;
  progress: number; // 0-100
  canGoBack: boolean;
  canGoNext: boolean;
  canSkip: boolean;
}

export interface OnboardingFlowState {
  sessionId: string;
  submissionId?: string;
  currentStep: number;
  currentStepName: StepName;
  stepHistory: string[];
  formData: Record<string, unknown>;
  serviceType: ServiceType;
  isComplete: boolean;
  startedAt: Date;
  lastActiveAt: Date;
}
```

## ✅ Validation Schemas

### Step-Specific Validation

```typescript
// Service Selection Step
export const serviceSelectionStepSchema = z.object({
  serviceType: serviceTypeSchema,
  serviceDetails: z.record(z.unknown()).optional(),
});

// Basic Information Step
export const basicInfoStepSchema = z.object({
  projectName: z.string().min(1, 'Project name is required'),
  companyName: z.string().min(1, 'Company name is required'),
  industry: z.string().min(1, 'Industry is required'),
  projectDescription: z.string().min(10, 'Project description must be at least 10 characters'),
  contactEmail: z.string().min(1, 'Email is required').email('Invalid email address'),
  contactPhone: z.string().optional(),
  preferredContact: z.enum(['email', 'phone', 'both']).default('email'),
});

// Service-Specific Requirements
export const landingPageRequirementsSchema = z.object({
  pageType: z.string().min(1, 'Page type is required'),
  designStyle: z.string().min(1, 'Design style is required'),
  sections: z.array(z.string()).min(1, 'At least one section is required'),
  ctaGoal: z.string().min(1, 'Call-to-action goal is required'),
  brandColors: z.string().optional(),
  competitorExamples: z.string().optional(),
  contentProvided: z.boolean().default(false),
});
```

### Dynamic Validation

```typescript
export function getStepValidationSchema(stepName: StepName, serviceType?: ServiceType) {
  const baseSchema = stepValidationSchemas[stepName];
  
  if (stepName === 'service_requirements' && serviceType) {
    switch (serviceType) {
      case 'landing_page':
        return landingPageRequirementsSchema;
      case 'web_app':
        return webAppRequirementsSchema;
      case 'mobile_app':
        return mobileAppRequirementsSchema;
      default:
        return baseSchema;
    }
  }
  
  return baseSchema;
}
```

## 🏗️ Flow Architecture

### 1. Step Configuration

Each step is configured with:
- **Validation Schema**: Zod schema for data validation
- **Form Configuration**: UI form field definitions
- **Flow Logic**: Conditions for navigation and display
- **Service Type Mapping**: Which services use this step

### 2. Progress Tracking

- Individual step progress is tracked in `onboarding_step_progress`
- Analytics are aggregated in `onboarding_analytics`
- Navigation history is maintained for UX analysis

### 3. Conditional Logic

Steps can be:
- **Service-Specific**: Only shown for certain service types
- **Conditional**: Shown based on previous step data
- **Skippable**: Can be skipped under certain conditions
- **Required**: Must be completed to proceed

## 🚀 Implementation Guide

### 1. Initialize Onboarding Flow

```typescript
// Start new onboarding session
const flowRequest: StartOnboardingFlowRequest = {
  serviceType: 'landing_page',
  userAgent: navigator.userAgent,
  deviceType: 'desktop'
};

const response = await startOnboardingFlow(flowRequest);
const { sessionId, flowConfig, currentStep } = response;
```

### 2. Submit Step Data

```typescript
// Submit step data with validation
const submitRequest: SubmitStepDataRequest = {
  sessionId,
  stepId: currentStep.id,
  stepData: formData,
  timeSpent: 120, // seconds
  deviceType: 'desktop'
};

const result = await submitStepData(submitRequest);
if (result.validationResult.isValid) {
  // Move to next step
  setCurrentStep(result.nextStep);
} else {
  // Show validation errors
  setErrors(result.validationResult.errors);
}
```

### 3. Track Analytics

```typescript
// Analytics are automatically tracked during the flow
const analytics = await getOnboardingAnalytics(sessionId);
console.log(`Completion rate: ${analytics.completionRate}%`);
console.log(`Average step time: ${analytics.averageStepTime}s`);
```

## 📊 API Endpoints

### Step Management

- `GET /api/onboarding/steps` - Get all steps
- `GET /api/onboarding/steps/:serviceType` - Get steps for service type
- `POST /api/onboarding/steps` - Create new step
- `PUT /api/onboarding/steps/:id` - Update step
- `DELETE /api/onboarding/steps/:id` - Delete step

### Flow Management

- `POST /api/onboarding/flow/start` - Start new flow
- `POST /api/onboarding/flow/submit` - Submit step data
- `GET /api/onboarding/flow/:sessionId` - Get flow state
- `POST /api/onboarding/flow/:sessionId/back` - Go back to previous step
- `POST /api/onboarding/flow/:sessionId/skip` - Skip current step

### Analytics

- `GET /api/onboarding/analytics/:sessionId` - Get session analytics
- `GET /api/onboarding/analytics/summary` - Get summary analytics
- `GET /api/onboarding/analytics/performance` - Get performance metrics

## 📈 Analytics & Tracking

### Metrics Tracked

1. **Completion Metrics**
   - Overall completion rate
   - Step-by-step completion rates
   - Abandonment points
   - Time to completion

2. **User Behavior**
   - Back navigation patterns
   - Error frequency and types
   - Help-seeking behavior
   - Retry patterns

3. **Performance Metrics**
   - Page load times
   - Form submission times
   - Error rates
   - Technical issues

4. **UX Metrics**
   - Step difficulty scores
   - User satisfaction indicators
   - Navigation efficiency
   - Mobile vs desktop performance

### Optimization Opportunities

- **High Abandonment Steps**: Identify and optimize problematic steps
- **Long Completion Times**: Simplify complex steps
- **High Error Rates**: Improve validation and user guidance
- **Device-Specific Issues**: Optimize for mobile/tablet experiences

## 🔧 Configuration Examples

### Example Step Configuration

```json
{
  "id": "basic_info_step",
  "stepNumber": 2,
  "stepName": "basic_info",
  "stepTitle": "Project Information",
  "stepDescription": "Tell us about your project and contact details",
  "componentType": "form",
  "serviceTypes": ["landing_page", "web_app", "mobile_app"],
  "validationSchema": {
    "type": "object",
    "properties": {
      "projectName": {"type": "string", "minLength": 1},
      "companyName": {"type": "string", "minLength": 1},
      "contactEmail": {"type": "string", "format": "email"}
    },
    "required": ["projectName", "companyName", "contactEmail"]
  },
  "formConfig": {
    "fields": [
      {
        "name": "projectName",
        "type": "text",
        "label": "Project Name",
        "required": true,
        "placeholder": "Enter your project name"
      },
      {
        "name": "companyName",
        "type": "text",
        "label": "Company Name",
        "required": true,
        "placeholder": "Enter your company name"
      }
    ],
    "layout": "two_column"
  },
  "uiLayout": "two_column",
  "displayOrder": 2,
  "progressWeight": 1,
  "estimatedTime": 3,
  "isActive": true,
  "isRequired": true,
  "backAllowed": true
}
```

### Example Analytics Output

```json
{
  "sessionId": "sess_abc123",
  "submissionId": "sub_def456",
  "totalSteps": 5,
  "completedSteps": 4,
  "skippedSteps": 0,
  "errorSteps": 1,
  "totalTimeSpent": 480,
  "averageStepTime": 96,
  "completionRate": 80,
  "conversionStatus": "in_progress",
  "backNavigationCount": 2,
  "errorCount": 3,
  "retryCount": 1,
  "deviceType": "desktop",
  "browserName": "Chrome",
  "performanceScore": 85,
  "userExperienceScore": 78
}
```

## 🎯 Best Practices

### 1. Step Design
- Keep steps focused on single objectives
- Minimize required fields per step
- Provide clear progress indicators
- Include helpful descriptions and examples

### 2. Validation
- Validate on both client and server side
- Provide immediate feedback on errors
- Use progressive validation for better UX
- Allow partial saving of step data

### 3. Analytics
- Track all user interactions
- Monitor performance across devices
- Set up alerts for high abandonment rates
- Use A/B testing for step optimization

### 4. Accessibility
- Ensure keyboard navigation works
- Provide screen reader support
- Use proper ARIA labels
- Maintain color contrast standards

This schema provides a comprehensive foundation for managing complex onboarding flows with detailed analytics and flexible configuration options.
