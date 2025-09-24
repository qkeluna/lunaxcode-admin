# Lunaxcode CMS - Content Tables Schema for Xata Migration

This document contains the complete schema definitions for all content tables that can be migrated from the current SQLite/D1 database to Xata.

## 🆔 Xata Default Fields

All tables will automatically include these Xata system fields:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `xata_id` | text | UNIQUE, NOT NULL | Xata's unique record identifier |
| `xata_version` | integer | NOT NULL | Record version for optimistic concurrency |
| `xata_createdat` | timestampz | NOT NULL | Automatic creation timestamp |
| `xata_updatedat` | timestampz | NOT NULL | Automatic update timestamp |

**Note:** These fields are managed automatically by Xata and should not be included in your application logic.

## 📊 Tables Overview

- **pricing_plans** - Service packages and pricing tiers
- **features** - Key product/service features displayed on landing page
- **process_steps** - Service workflow and process steps
- **hero_section** - Landing page hero content and CTAs
- **testimonials** - Client testimonials and reviews
- **contact_info** - Contact details and social media links
- **faqs** - Frequently asked questions
- **site_settings** - Global site configuration settings
- **addon_services** - Additional services and add-ons

---

## 1. pricing_plans

**Purpose:** Manages service packages and pricing tiers for different service categories.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `xata_id` | text | UNIQUE, NOT NULL | auto-generated | Xata's unique record identifier |
| `xata_version` | integer | NOT NULL | auto-generated | Record version for optimistic concurrency |
| `xata_createdat` | timestampz | NOT NULL | auto-generated | Automatic creation timestamp |
| `xata_updatedat` | timestampz | NOT NULL | auto-generated | Automatic update timestamp |
| `planId` | text | NOT NULL | - | Custom identifier for pricing plan (e.g., "landing_basic") |
| `name` | text | NOT NULL | - | Display name of the pricing plan |
| `price` | text | NOT NULL | - | Price display text (e.g., "₱9,999", "Starting at ₱19,999") |
| `period` | text | - | '' | Billing period (e.g., "one-time", "monthly") |
| `description` | text | NOT NULL | - | Short description of the plan |
| `features` | json | NOT NULL | - | Array of plan features |
| `buttonText` | text | NOT NULL | 'Get Started' | CTA button text |
| `buttonVariant` | text | NOT NULL | 'outline' | Button style variant |
| `popular` | boolean | NOT NULL | false | Whether this plan is marked as popular |
| `timeline` | text | NOT NULL | - | Delivery timeline (e.g., "48 hours", "1-2 weeks") |
| `displayOrder` | integer | NOT NULL | 0 | Order for displaying plans |
| `category` | text | - | 'web' | Plan category: 'web', 'mobile' |
| `isActive` | boolean | NOT NULL | true | Whether plan is active/visible |

**Sample Data:**
```json
{
  "planId": "landing_basic",
  "name": "Landing Page Basic",
  "price": "₱9,999",
  "period": "one-time",
  "description": "Perfect for small businesses needing a professional online presence",
  "features": ["Custom design", "Mobile responsive", "Contact form", "SEO optimized"],
  "buttonText": "Get Started",
  "buttonVariant": "outline",
  "popular": false,
  "timeline": "48 hours",
  "displayOrder": 1,
  "category": "web",
  "isActive": true
}
```

---

## 2. features

**Purpose:** Manages key features displayed on the landing page to highlight service capabilities.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `xata_id` | text | UNIQUE, NOT NULL | auto-generated | Xata's unique record identifier |
| `xata_version` | integer | NOT NULL | auto-generated | Record version for optimistic concurrency |
| `xata_createdat` | timestampz | NOT NULL | auto-generated | Automatic creation timestamp |
| `xata_updatedat` | timestampz | NOT NULL | auto-generated | Automatic update timestamp |
| `title` | text | NOT NULL | - | Feature title/headline |
| `description` | text | NOT NULL | - | Feature description text |
| `icon` | text | NOT NULL | - | Lucide icon name (e.g., "Zap", "Shield") |
| `color` | text | NOT NULL | - | CSS gradient classes for styling |
| `displayOrder` | integer | NOT NULL | 0 | Order for displaying features |
| `isActive` | boolean | NOT NULL | true | Whether feature is active/visible |

**Sample Data:**
```json
{
  "title": "Lightning Fast Delivery",
  "description": "Get your professional website delivered in just 48 hours",
  "icon": "Zap",
  "color": "bg-gradient-to-r from-blue-500 to-purple-600",
  "displayOrder": 1,
  "isActive": true
}
```

---

## 3. process_steps

**Purpose:** Defines the service workflow and process steps shown to clients.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `xata_id` | text | UNIQUE, NOT NULL | auto-generated | Xata's unique record identifier |
| `xata_version` | integer | NOT NULL | auto-generated | Record version for optimistic concurrency |
| `xata_createdat` | timestampz | NOT NULL | auto-generated | Automatic creation timestamp |
| `xata_updatedat` | timestampz | NOT NULL | auto-generated | Automatic update timestamp |
| `stepNumber` | integer | NOT NULL | - | Step sequence number |
| `title` | text | NOT NULL | - | Step title/name |
| `description` | text | NOT NULL | - | Step description |
| `icon` | text | NOT NULL | - | Lucide icon name for step |
| `details` | json | - | - | Additional details/sub-points array |
| `displayOrder` | integer | NOT NULL | 0 | Order for displaying steps |
| `isActive` | boolean | NOT NULL | true | Whether step is active/visible |

**Sample Data:**
```json
{
  "stepNumber": 1,
  "title": "Discovery & Planning",
  "description": "We analyze your requirements and create a detailed project plan",
  "icon": "Search",
  "details": ["Requirements gathering", "Competitor analysis", "Project timeline"],
  "displayOrder": 1,
  "isActive": true
}
```

---

## 4. hero_section

**Purpose:** Manages the main hero section content on the landing page.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `xata_id` | text | UNIQUE, NOT NULL | auto-generated | Xata's unique record identifier |
| `xata_version` | integer | NOT NULL | auto-generated | Record version for optimistic concurrency |
| `xata_createdat` | timestampz | NOT NULL | auto-generated | Automatic creation timestamp |
| `xata_updatedat` | timestampz | NOT NULL | auto-generated | Automatic update timestamp |
| `headline` | text | NOT NULL | - | Main hero headline |
| `subheadline` | text | NOT NULL | - | Supporting hero text |
| `ctaText` | text | NOT NULL | 'Get Started' | Primary CTA button text |
| `ctaVariant` | text | NOT NULL | 'default' | Primary CTA button style |
| `secondaryCtaText` | text | - | - | Secondary CTA button text |
| `secondaryCtaVariant` | text | - | 'outline' | Secondary CTA button style |
| `backgroundVideo` | text | - | - | URL to background video |
| `isActive` | boolean | NOT NULL | true | Whether section is active |

**Sample Data:**
```json
{
  "headline": "Professional Websites Delivered in 48 Hours",
  "subheadline": "Get your business online fast with our expert web development team",
  "ctaText": "Start Your Project",
  "ctaVariant": "default",
  "secondaryCtaText": "View Portfolio",
  "secondaryCtaVariant": "outline",
  "backgroundVideo": null,
  "isActive": true
}
```

---

## 5. testimonials

**Purpose:** Manages client testimonials and reviews displayed on the website.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `xata_id` | text | UNIQUE, NOT NULL | auto-generated | Xata's unique record identifier |
| `xata_version` | integer | NOT NULL | auto-generated | Record version for optimistic concurrency |
| `xata_createdat` | timestampz | NOT NULL | auto-generated | Automatic creation timestamp |
| `xata_updatedat` | timestampz | NOT NULL | auto-generated | Automatic update timestamp |
| `clientName` | text | NOT NULL | - | Client's full name |
| `clientCompany` | text | - | - | Client's company name |
| `clientRole` | text | - | - | Client's job title/role |
| `testimonial` | text | NOT NULL | - | Testimonial content/quote |
| `rating` | integer | NOT NULL | 5 | Star rating (1-5) |
| `avatar` | text | - | - | URL to client's avatar image |
| `projectType` | text | - | - | Type: 'landing_page', 'web_app', 'mobile_app' |
| `displayOrder` | integer | NOT NULL | 0 | Order for displaying testimonials |
| `isActive` | boolean | NOT NULL | true | Whether testimonial is active/visible |

**Sample Data:**
```json
{
  "clientName": "Maria Santos",
  "clientCompany": "Santos Bakery",
  "clientRole": "Owner",
  "testimonial": "Lunaxcode delivered our website in just 2 days! Amazing quality and service.",
  "rating": 5,
  "avatar": "/avatars/maria-santos.jpg",
  "projectType": "landing_page",
  "displayOrder": 1,
  "isActive": true
}
```

---

## 6. contact_info

**Purpose:** Manages contact information and social media links.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `xata_id` | text | UNIQUE, NOT NULL | auto-generated | Xata's unique record identifier |
| `xata_version` | integer | NOT NULL | auto-generated | Record version for optimistic concurrency |
| `xata_createdat` | timestampz | NOT NULL | auto-generated | Automatic creation timestamp |
| `xata_updatedat` | timestampz | NOT NULL | auto-generated | Automatic update timestamp |
| `type` | text | NOT NULL | - | Contact type: 'email', 'phone', 'address', 'social' |
| `label` | text | NOT NULL | - | Display label for contact info |
| `value` | text | NOT NULL | - | Contact value (email, phone, URL, etc.) |
| `icon` | text | - | - | Lucide icon name |
| `isPrimary` | boolean | NOT NULL | false | Whether this is primary contact method |
| `displayOrder` | integer | NOT NULL | 0 | Order for displaying contact info |
| `isActive` | boolean | NOT NULL | true | Whether contact info is active/visible |

**Sample Data:**
```json
{
  "type": "email",
  "label": "Email",
  "value": "hello@lunaxcode.com",
  "icon": "Mail",
  "isPrimary": true,
  "displayOrder": 1,
  "isActive": true
}
```

---

## 7. faqs

**Purpose:** Manages frequently asked questions displayed on the website.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `xata_id` | text | UNIQUE, NOT NULL | auto-generated | Xata's unique record identifier |
| `xata_version` | integer | NOT NULL | auto-generated | Record version for optimistic concurrency |
| `xata_createdat` | timestampz | NOT NULL | auto-generated | Automatic creation timestamp |
| `xata_updatedat` | timestampz | NOT NULL | auto-generated | Automatic update timestamp |
| `question` | text | NOT NULL | - | FAQ question |
| `answer` | text | NOT NULL | - | FAQ answer (supports markdown) |
| `category` | text | - | - | FAQ category: 'pricing', 'process', 'general', 'technical' |
| `displayOrder` | integer | NOT NULL | 0 | Order for displaying FAQs |
| `isActive` | boolean | NOT NULL | true | Whether FAQ is active/visible |

**Sample Data:**
```json
{
  "question": "How long does it take to build a website?",
  "answer": "Our landing pages are delivered in 48 hours, while full websites take 1-3 weeks depending on complexity.",
  "category": "process",
  "displayOrder": 1,
  "isActive": true
}
```

---

## 8. site_settings

**Purpose:** Manages global site configuration and settings.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `xata_id` | text | UNIQUE, NOT NULL | auto-generated | Xata's unique record identifier |
| `xata_version` | integer | NOT NULL | auto-generated | Record version for optimistic concurrency |
| `xata_createdat` | timestampz | NOT NULL | auto-generated | Automatic creation timestamp |
| `xata_updatedat` | timestampz | NOT NULL | auto-generated | Automatic update timestamp |
| `key` | text | NOT NULL, UNIQUE | - | Setting key/name |
| `value` | text | NOT NULL | - | Setting value |
| `type` | text | NOT NULL | 'text' | Value type: 'text', 'number', 'boolean', 'json' |
| `description` | text | - | - | Setting description |
| `isPublic` | boolean | NOT NULL | true | Whether setting is publicly accessible |

**Sample Data:**
```json
{
  "key": "site_title",
  "value": "Lunaxcode - Professional Web Development",
  "type": "text",
  "description": "Main site title used in meta tags",
  "isPublic": true
}
```

---

## 9. addon_services

**Purpose:** Manages additional services and add-ons available to clients.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `xata_id` | text | UNIQUE, NOT NULL | auto-generated | Xata's unique record identifier |
| `xata_version` | integer | NOT NULL | auto-generated | Record version for optimistic concurrency |
| `xata_createdat` | timestampz | NOT NULL | auto-generated | Automatic creation timestamp |
| `xata_updatedat` | timestampz | NOT NULL | auto-generated | Automatic update timestamp |
| `serviceId` | text | NOT NULL | - | Custom identifier for add-on service (e.g., "seo_basic") |
| `name` | text | NOT NULL | - | Service name |
| `price` | text | NOT NULL | - | Price display text |
| `description` | text | NOT NULL | - | Service description |
| `unit` | text | - | - | Pricing unit: 'per page', 'per month', 'one-time' |
| `category` | text | - | 'general' | Category: 'general', 'seo', 'maintenance', 'integration' |
| `icon` | text | - | - | Lucide icon name |
| `popular` | boolean | NOT NULL | false | Whether service is popular/featured |
| `displayOrder` | integer | NOT NULL | 0 | Order for displaying services |
| `isActive` | boolean | NOT NULL | true | Whether service is active/available |

**Sample Data:**
```json
{
  "serviceId": "seo_basic",
  "name": "Basic SEO Optimization",
  "price": "₱2,999",
  "description": "On-page SEO optimization for better search visibility",
  "unit": "one-time",
  "category": "seo",
  "icon": "Search",
  "popular": true,
  "displayOrder": 1,
  "isActive": true
}
```

---

## 🔄 Migration Notes

### Data Types Mapping for Xata

| Current SQLite Type | Xata Type | Notes |
|-------------------|-----------|-------|
| `text` | `string` | Direct mapping |
| `integer` | `int` | Direct mapping |
| `boolean` (SQLite integer) | `bool` | Convert 0/1 to false/true |
| `text` (JSON strings) | `json` | Parse JSON strings before migration |
| `timestampz` | `datetime` | Xata native timestamp with timezone |

### Special Considerations

1. **Xata System Fields**: All tables automatically get `xata_id`, `xata_version`, `xata_createdat`, `xata_updatedat`
2. **JSON Fields**: Convert JSON strings to native JSON objects:
   - `pricing_plans.features` - Array of plan features
   - `process_steps.details` - Array of additional step details
3. **Custom Identifiers**: Use business-friendly IDs:
   - `pricing_plans.planId` - For referencing plans in code
   - `addon_services.serviceId` - For referencing services in code
4. **Display Order**: All tables use `displayOrder` for custom sorting
5. **Soft Deletes**: All tables use `isActive` instead of hard deletes
6. **Categories**: Many tables have category fields for filtering/grouping

### Xata Indexes (automatically optimized)

Xata automatically optimizes queries, but these fields are commonly queried:

- `pricing_plans`: `category`, `isActive`, `displayOrder`
- `features`: `displayOrder`, `isActive`
- `process_steps`: `displayOrder`, `isActive`, `stepNumber`
- `testimonials`: `projectType`, `isActive`, `displayOrder`
- `contact_info`: `type`, `isActive`, `isPrimary`
- `faqs`: `category`, `isActive`, `displayOrder`
- `addon_services`: `category`, `isActive`, `popular`
- `site_settings`: `key`, `isPublic`

---

## 📊 Total Records Estimate

Based on typical usage:
- **pricing_plans**: ~6-12 records
- **features**: ~6-8 records  
- **process_steps**: ~4-6 records
- **hero_section**: ~1-3 records
- **testimonials**: ~10-20 records
- **contact_info**: ~5-10 records
- **faqs**: ~15-25 records
- **site_settings**: ~20-30 records
- **addon_services**: ~8-15 records

**Total estimated records**: ~75-130 records across all content tables.

## 🎯 Xata Migration Benefits

### Automatic Features
- ✅ **Auto-generated IDs**: `xata_id` replaces custom ID management
- ✅ **Version Control**: `xata_version` for optimistic concurrency
- ✅ **Timestamps**: Automatic `xata_createdat` and `xata_updatedat`
- ✅ **Query Optimization**: Built-in indexing and caching
- ✅ **TypeScript SDK**: Auto-generated types and client
- ✅ **Real-time Updates**: Built-in subscriptions and webhooks

### Developer Experience
- 🔧 **No Schema Migrations**: Schema changes via dashboard
- 🔧 **Built-in Admin UI**: Browse and edit data directly
- 🔧 **API First**: RESTful and GraphQL APIs included
- 🔧 **File Storage**: Built-in file attachments support
- 🔧 **Branch-based Development**: Database branching like Git

### Performance Benefits
- ⚡ **Global CDN**: Data served from edge locations
- ⚡ **Auto-scaling**: Handles traffic spikes automatically
- ⚡ **Caching**: Intelligent query caching built-in
- ⚡ **Search**: Full-text search capabilities included
