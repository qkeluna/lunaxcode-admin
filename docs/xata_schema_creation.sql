-- Lunaxcode CMS - Xata Database Schema Creation Script
-- Copy and paste this entire script into Xata's queries console
-- 
-- IMPORTANT NOTES:
-- - This script explicitly includes xata_id (PRIMARY KEY), xata_version, xata_createdat, xata_updatedat in all tables
-- - xata_id serves as the unique identifier and primary key for each record
-- - All Xata system fields are included with proper defaults and constraints
-- - This script will DROP existing tables and recreate them with sample data
-- - Use with caution in production environments

-- Start transaction for safe execution
BEGIN;

-- ==========================================================================
-- DROP EXISTING TABLES (if they exist)
-- ==========================================================================
DROP TABLE IF EXISTS pricing_plans CASCADE;
DROP TABLE IF EXISTS features CASCADE;
DROP TABLE IF EXISTS process_steps CASCADE;
DROP TABLE IF EXISTS hero_section CASCADE;
DROP TABLE IF EXISTS testimonials CASCADE;
DROP TABLE IF EXISTS contact_info CASCADE;
DROP TABLE IF EXISTS faqs CASCADE;
DROP TABLE IF EXISTS site_settings CASCADE;
DROP TABLE IF EXISTS addon_services CASCADE;

-- ==========================================================================
-- 1. PRICING PLANS TABLE
-- ==========================================================================
CREATE TABLE pricing_plans (
    "xata_id" TEXT PRIMARY KEY NOT NULL,
    "xata_version" INTEGER NOT NULL DEFAULT 0,
    "xata_createdat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "xata_updatedat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "planId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "price" TEXT NOT NULL,
    "period" TEXT DEFAULT '',
    "description" TEXT NOT NULL,
    "features" JSON NOT NULL,
    "buttonText" TEXT NOT NULL DEFAULT 'Get Started',
    "buttonVariant" TEXT NOT NULL DEFAULT 'outline',
    "popular" BOOLEAN NOT NULL DEFAULT false,
    "timeline" TEXT NOT NULL,
    "displayOrder" INTEGER NOT NULL DEFAULT 0,
    "category" TEXT DEFAULT 'web',
    "isActive" BOOLEAN NOT NULL DEFAULT true
);

-- Sample data for pricing_plans
INSERT INTO pricing_plans (
    "xata_id", "xata_version", "xata_createdat", "xata_updatedat",
    "planId", "name", "price", "period", "description", "features", 
    "buttonText", "buttonVariant", "popular", "timeline", "displayOrder", "category", "isActive"
) VALUES 
(
    'rec_landing_basic_001',
    0,
    NOW(),
    NOW(),
    'landing_basic',
    'Landing Page Basic',
    '₱9,999',
    'one-time',
    'Perfect for small businesses needing a professional online presence',
    '["Custom design", "Mobile responsive", "Contact form", "SEO optimized", "48-hour delivery"]',
    'Get Started',
    'outline',
    false,
    '48 hours',
    1,
    'web',
    true
),
(
    'rec_landing_premium_002',
    0,
    NOW(),
    NOW(),
    'landing_premium',
    'Landing Page Premium',
    '₱19,999',
    'one-time',
    'Advanced landing page with interactive elements and animations',
    '["Everything in Basic", "Advanced animations", "Interactive elements", "A/B testing setup", "Analytics integration"]',
    'Choose Premium',
    'default',
    true,
    '72 hours',
    2,
    'web',
    true
),
(
    'rec_webapp_starter_003',
    0,
    NOW(),
    NOW(),
    'webapp_starter',
    'Web App Starter',
    'Starting at ₱49,999',
    'project-based',
    'Full-featured web application with user authentication',
    '["User authentication", "Admin dashboard", "Database integration", "API development", "Responsive design"]',
    'Start Project',
    'default',
    false,
    '1-2 weeks',
    3,
    'web',
    true
);

-- ==========================================================================
-- 2. FEATURES TABLE
-- ==========================================================================
CREATE TABLE features (
    "xata_id" TEXT PRIMARY KEY NOT NULL,
    "xata_version" INTEGER NOT NULL DEFAULT 0,
    "xata_createdat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "xata_updatedat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "icon" TEXT NOT NULL,
    "color" TEXT NOT NULL,
    "displayOrder" INTEGER NOT NULL DEFAULT 0,
    "isActive" BOOLEAN NOT NULL DEFAULT true
);

-- Sample data for features
INSERT INTO features (
    "xata_id", "xata_version", "xata_createdat", "xata_updatedat",
    "title", "description", "icon", "color", "displayOrder", "isActive"
) VALUES 
(
    'rec_feature_fast_001',
    0,
    NOW(),
    NOW(),
    'Lightning Fast Delivery',
    'Get your professional website delivered in just 48 hours with our streamlined development process',
    'Zap',
    'bg-gradient-to-r from-blue-500 to-purple-600',
    1,
    true
),
(
    'rec_feature_mobile_002',
    0,
    NOW(),
    NOW(),
    'Mobile-First Design',
    'Every website is designed mobile-first to ensure perfect user experience across all devices',
    'Smartphone',
    'bg-gradient-to-r from-green-500 to-teal-600',
    2,
    true
),
(
    'rec_feature_seo_003',
    0,
    NOW(),
    NOW(),
    'SEO Optimized',
    'Built-in SEO optimization to help your website rank higher in search engine results',
    'Search',
    'bg-gradient-to-r from-orange-500 to-red-600',
    3,
    true
),
(
    'rec_feature_secure_004',
    0,
    NOW(),
    NOW(),
    'Secure & Reliable',
    'Enterprise-grade security and 99.9% uptime guarantee for your peace of mind',
    'Shield',
    'bg-gradient-to-r from-purple-500 to-pink-600',
    4,
    true
);

-- ==========================================================================
-- 3. PROCESS STEPS TABLE
-- ==========================================================================
CREATE TABLE process_steps (
    "xata_id" TEXT PRIMARY KEY NOT NULL,
    "xata_version" INTEGER NOT NULL DEFAULT 0,
    "xata_createdat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "xata_updatedat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "stepNumber" INTEGER NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "icon" TEXT NOT NULL,
    "details" JSON,
    "displayOrder" INTEGER NOT NULL DEFAULT 0,
    "isActive" BOOLEAN NOT NULL DEFAULT true
);

-- Sample data for process_steps
INSERT INTO process_steps (
    "xata_id", "xata_version", "xata_createdat", "xata_updatedat",
    "stepNumber", "title", "description", "icon", "details", "displayOrder", "isActive"
) VALUES 
(
    'rec_step_discovery_001',
    0,
    NOW(),
    NOW(),
    1,
    'Discovery & Planning',
    'We analyze your requirements and create a detailed project plan tailored to your business goals',
    'Search',
    '["Requirements gathering", "Competitor analysis", "Project timeline", "Technology selection"]',
    1,
    true
),
(
    'rec_step_design_002',
    0,
    NOW(),
    NOW(),
    2,
    'Design & Prototyping',
    'Create stunning visual designs and interactive prototypes for your approval',
    'Palette',
    '["Wireframe creation", "Visual design", "Interactive prototype", "Client feedback integration"]',
    2,
    true
),
(
    'rec_step_development_003',
    0,
    NOW(),
    NOW(),
    3,
    'Development & Testing',
    'Build your website using modern technologies with rigorous testing procedures',
    'Code',
    '["Frontend development", "Backend integration", "Quality assurance", "Performance optimization"]',
    3,
    true
),
(
    'rec_step_launch_004',
    0,
    NOW(),
    NOW(),
    4,
    'Launch & Support',
    'Deploy your website and provide ongoing support for smooth operations',
    'Rocket',
    '["Domain setup", "SSL certificate", "Launch deployment", "Post-launch support"]',
    4,
    true
);

-- ==========================================================================
-- 4. HERO SECTION TABLE
-- ==========================================================================
CREATE TABLE hero_section (
    "xata_id" TEXT PRIMARY KEY NOT NULL,
    "xata_version" INTEGER NOT NULL DEFAULT 0,
    "xata_createdat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "xata_updatedat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "headline" TEXT NOT NULL,
    "subheadline" TEXT NOT NULL,
    "ctaText" TEXT NOT NULL DEFAULT 'Get Started',
    "ctaVariant" TEXT NOT NULL DEFAULT 'default',
    "secondaryCtaText" TEXT,
    "secondaryCtaVariant" TEXT DEFAULT 'outline',
    "backgroundVideo" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT true
);

-- Sample data for hero_section
INSERT INTO hero_section (
    "xata_id", "xata_version", "xata_createdat", "xata_updatedat",
    "headline", "subheadline", "ctaText", "ctaVariant", 
    "secondaryCtaText", "secondaryCtaVariant", "backgroundVideo", "isActive"
) VALUES 
(
    'rec_hero_main_001',
    0,
    NOW(),
    NOW(),
    'Professional Websites Delivered in 48 Hours',
    'Get your business online fast with our expert web development team. From landing pages to full web applications, we deliver quality results quickly.',
    'Start Your Project',
    'default',
    'View Portfolio',
    'outline',
    null,
    true
);

-- ==========================================================================
-- 5. TESTIMONIALS TABLE
-- ==========================================================================
CREATE TABLE testimonials (
    "xata_id" TEXT PRIMARY KEY NOT NULL,
    "xata_version" INTEGER NOT NULL DEFAULT 0,
    "xata_createdat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "xata_updatedat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "clientName" TEXT NOT NULL,
    "clientCompany" TEXT,
    "clientRole" TEXT,
    "testimonial" TEXT NOT NULL,
    "rating" INTEGER NOT NULL DEFAULT 5,
    "avatar" TEXT,
    "projectType" TEXT,
    "displayOrder" INTEGER NOT NULL DEFAULT 0,
    "isActive" BOOLEAN NOT NULL DEFAULT true
);

-- Sample data for testimonials
INSERT INTO testimonials (
    "xata_id", "xata_version", "xata_createdat", "xata_updatedat",
    "clientName", "clientCompany", "clientRole", "testimonial", "rating", 
    "avatar", "projectType", "displayOrder", "isActive"
) VALUES 
(
    'rec_testimonial_maria_001',
    0,
    NOW(),
    NOW(),
    'Maria Santos',
    'Santos Bakery',
    'Owner',
    'Lunaxcode delivered our website in just 2 days! The quality exceeded our expectations and our online orders increased by 300% in the first month.',
    5,
    '/avatars/maria-santos.jpg',
    'landing_page',
    1,
    true
),
(
    'rec_testimonial_juan_002',
    0,
    NOW(),
    NOW(),
    'Juan Dela Cruz',
    'TechStart Solutions',
    'CEO',
    'The team at Lunaxcode built our complete web application with user authentication and admin dashboard. Professional service and excellent communication throughout.',
    5,
    '/avatars/juan-delacruz.jpg',
    'web_app',
    2,
    true
),
(
    'rec_testimonial_anna_003',
    0,
    NOW(),
    NOW(),
    'Anna Garcia',
    'Creative Studio PH',
    'Creative Director',
    'Amazing work on our portfolio website. The design is stunning and the mobile experience is flawless. Highly recommend Lunaxcode!',
    5,
    '/avatars/anna-garcia.jpg',
    'landing_page',
    3,
    true
);

-- ==========================================================================
-- 6. CONTACT INFO TABLE
-- ==========================================================================
CREATE TABLE contact_info (
    "xata_id" TEXT PRIMARY KEY NOT NULL,
    "xata_version" INTEGER NOT NULL DEFAULT 0,
    "xata_createdat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "xata_updatedat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "type" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "icon" TEXT,
    "isPrimary" BOOLEAN NOT NULL DEFAULT false,
    "displayOrder" INTEGER NOT NULL DEFAULT 0,
    "isActive" BOOLEAN NOT NULL DEFAULT true
);

-- Sample data for contact_info
INSERT INTO contact_info (
    "xata_id", "xata_version", "xata_createdat", "xata_updatedat",
    "type", "label", "value", "icon", "isPrimary", "displayOrder", "isActive"
) VALUES 
(
    'rec_contact_email_001',
    0,
    NOW(),
    NOW(),
    'email',
    'Email',
    'hello@lunaxcode.com',
    'Mail',
    true,
    1,
    true
),
(
    'rec_contact_phone_002',
    0,
    NOW(),
    NOW(),
    'phone',
    'Phone',
    '+63 917 123 4567',
    'Phone',
    true,
    2,
    true
),
(
    'rec_contact_facebook_003',
    0,
    NOW(),
    NOW(),
    'social',
    'Facebook',
    'https://facebook.com/lunaxcode',
    'Facebook',
    false,
    3,
    true
),
(
    'rec_contact_linkedin_004',
    0,
    NOW(),
    NOW(),
    'social',
    'LinkedIn',
    'https://linkedin.com/company/lunaxcode',
    'Linkedin',
    false,
    4,
    true
),
(
    'rec_contact_office_005',
    0,
    NOW(),
    NOW(),
    'address',
    'Office',
    'Makati City, Metro Manila, Philippines',
    'MapPin',
    false,
    5,
    true
);

-- ==========================================================================
-- 7. FAQS TABLE
-- ==========================================================================
CREATE TABLE faqs (
    "xata_id" TEXT PRIMARY KEY NOT NULL,
    "xata_version" INTEGER NOT NULL DEFAULT 0,
    "xata_createdat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "xata_updatedat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "question" TEXT NOT NULL,
    "answer" TEXT NOT NULL,
    "category" TEXT,
    "displayOrder" INTEGER NOT NULL DEFAULT 0,
    "isActive" BOOLEAN NOT NULL DEFAULT true
);

-- Sample data for faqs
INSERT INTO faqs (
    "xata_id", "xata_version", "xata_createdat", "xata_updatedat",
    "question", "answer", "category", "displayOrder", "isActive"
) VALUES 
(
    'rec_faq_timeline_001',
    0,
    NOW(),
    NOW(),
    'How long does it take to build a website?',
    'Our landing pages are delivered in 48 hours, while full websites take 1-3 weeks depending on complexity. We provide a detailed timeline during the initial consultation.',
    'process',
    1,
    true
),
(
    'rec_faq_package_002',
    0,
    NOW(),
    NOW(),
    'What is included in the basic landing page package?',
    'The basic package includes custom design, mobile responsiveness, contact form, SEO optimization, and 48-hour delivery. You also get free hosting for the first month.',
    'pricing',
    2,
    true
),
(
    'rec_faq_support_003',
    0,
    NOW(),
    NOW(),
    'Do you provide ongoing support after launch?',
    'Yes! We provide 30 days of free support after launch, including bug fixes and minor content updates. Extended support packages are also available.',
    'general',
    3,
    true
),
(
    'rec_faq_branding_004',
    0,
    NOW(),
    NOW(),
    'Can you work with my existing brand guidelines?',
    'Absolutely! We can work with your existing brand colors, fonts, and style guide to ensure consistency across all your marketing materials.',
    'general',
    4,
    true
),
(
    'rec_faq_tech_005',
    0,
    NOW(),
    NOW(),
    'What technologies do you use?',
    'We use modern technologies like React, Next.js, TypeScript, and FastAPI to build fast, secure, and maintainable websites and applications.',
    'technical',
    5,
    true
),
(
    'rec_faq_payment_006',
    0,
    NOW(),
    NOW(),
    'Do you offer payment plans?',
    'Yes, we offer flexible payment options including 50% upfront and 50% upon completion for projects over ₱20,000. Contact us to discuss your specific needs.',
    'pricing',
    6,
    true
);

-- ==========================================================================
-- 8. SITE SETTINGS TABLE
-- ==========================================================================
CREATE TABLE site_settings (
    "xata_id" TEXT PRIMARY KEY NOT NULL,
    "xata_version" INTEGER NOT NULL DEFAULT 0,
    "xata_createdat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "xata_updatedat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "key" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "type" TEXT NOT NULL DEFAULT 'text',
    "description" TEXT,
    "isPublic" BOOLEAN NOT NULL DEFAULT true
);

-- Sample data for site_settings
INSERT INTO site_settings (
    "xata_id", "xata_version", "xata_createdat", "xata_updatedat",
    "key", "value", "type", "description", "isPublic"
) VALUES 
(
    'rec_setting_title_001',
    0,
    NOW(),
    NOW(),
    'site_title',
    'Lunaxcode - Professional Web Development',
    'text',
    'Main site title used in meta tags',
    true
),
(
    'rec_setting_description_002',
    0,
    NOW(),
    NOW(),
    'site_description',
    'Professional web development services in the Philippines. Get your website delivered in 48 hours with our expert team.',
    'text',
    'Site description for SEO',
    true
),
(
    'rec_setting_company_003',
    0,
    NOW(),
    NOW(),
    'company_name',
    'Lunaxcode',
    'text',
    'Company name displayed throughout the site',
    true
),
(
    'rec_setting_tagline_004',
    0,
    NOW(),
    NOW(),
    'company_tagline',
    'Fast. Professional. Reliable.',
    'text',
    'Company tagline or slogan',
    true
),
(
    'rec_setting_primary_005',
    0,
    NOW(),
    NOW(),
    'primary_color',
    '#3B82F6',
    'text',
    'Primary brand color in hex format',
    true
),
(
    'rec_setting_secondary_006',
    0,
    NOW(),
    NOW(),
    'secondary_color',
    '#8B5CF6',
    'text',
    'Secondary brand color in hex format',
    true
),
(
    'rec_setting_chat_007',
    0,
    NOW(),
    NOW(),
    'enable_chat',
    'true',
    'boolean',
    'Enable/disable live chat widget',
    true
),
(
    'rec_setting_analytics_008',
    0,
    NOW(),
    NOW(),
    'google_analytics_id',
    'G-XXXXXXXXXX',
    'text',
    'Google Analytics measurement ID',
    false
),
(
    'rec_setting_pixel_009',
    0,
    NOW(),
    NOW(),
    'facebook_pixel_id',
    '',
    'text',
    'Facebook Pixel ID for tracking',
    false
),
(
    'rec_setting_maintenance_010',
    0,
    NOW(),
    NOW(),
    'maintenance_mode',
    'false',
    'boolean',
    'Enable maintenance mode',
    false
);

-- ==========================================================================
-- 9. ADDON SERVICES TABLE
-- ==========================================================================
CREATE TABLE addon_services (
    "xata_id" TEXT PRIMARY KEY NOT NULL,
    "xata_version" INTEGER NOT NULL DEFAULT 0,
    "xata_createdat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "xata_updatedat" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "serviceId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "price" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "unit" TEXT,
    "category" TEXT DEFAULT 'general',
    "icon" TEXT,
    "popular" BOOLEAN NOT NULL DEFAULT false,
    "displayOrder" INTEGER NOT NULL DEFAULT 0,
    "isActive" BOOLEAN NOT NULL DEFAULT true
);

-- Sample data for addon_services
INSERT INTO addon_services (
    "xata_id", "xata_version", "xata_createdat", "xata_updatedat",
    "serviceId", "name", "price", "description", "unit", "category", 
    "icon", "popular", "displayOrder", "isActive"
) VALUES 
(
    'rec_addon_seo_001',
    0,
    NOW(),
    NOW(),
    'seo_basic',
    'Basic SEO Optimization',
    '₱2,999',
    'On-page SEO optimization including meta tags, structured data, and sitemap generation',
    'one-time',
    'seo',
    'Search',
    true,
    1,
    true
),
(
    'rec_addon_analytics_002',
    0,
    NOW(),
    NOW(),
    'analytics_setup',
    'Analytics & Tracking Setup',
    '₱1,999',
    'Google Analytics, Facebook Pixel, and conversion tracking implementation',
    'one-time',
    'integration',
    'BarChart3',
    false,
    2,
    true
),
(
    'rec_addon_cms_003',
    0,
    NOW(),
    NOW(),
    'content_management',
    'Content Management System',
    '₱8,999',
    'Custom CMS for easy content updates without technical knowledge',
    'one-time',
    'general',
    'FileText',
    true,
    3,
    true
),
(
    'rec_addon_ecommerce_004',
    0,
    NOW(),
    NOW(),
    'ecommerce_basic',
    'E-commerce Integration',
    '₱15,999',
    'PayMongo payment integration with product catalog and shopping cart',
    'one-time',
    'integration',
    'ShoppingCart',
    false,
    4,
    true
),
(
    'rec_addon_maintenance_005',
    0,
    NOW(),
    NOW(),
    'maintenance_monthly',
    'Monthly Maintenance',
    '₱2,499',
    'Regular updates, security patches, and performance monitoring',
    'per month',
    'maintenance',
    'Settings',
    true,
    5,
    true
),
(
    'rec_addon_ssl_006',
    0,
    NOW(),
    NOW(),
    'ssl_certificate',
    'SSL Certificate',
    '₱999',
    'Premium SSL certificate for enhanced security and trust',
    'per year',
    'general',
    'Shield',
    false,
    6,
    true
);

-- ==========================================================================
-- VERIFICATION QUERIES
-- ==========================================================================
-- Run these queries to verify that all tables were created successfully:

-- Check table creation
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

-- Verify sample data insertion
SELECT 'pricing_plans' as table_name, COUNT(*) as record_count FROM pricing_plans
UNION ALL
SELECT 'features', COUNT(*) FROM features
UNION ALL
SELECT 'process_steps', COUNT(*) FROM process_steps
UNION ALL
SELECT 'hero_section', COUNT(*) FROM hero_section
UNION ALL
SELECT 'testimonials', COUNT(*) FROM testimonials
UNION ALL
SELECT 'contact_info', COUNT(*) FROM contact_info
UNION ALL
SELECT 'faqs', COUNT(*) FROM faqs
UNION ALL
SELECT 'site_settings', COUNT(*) FROM site_settings
UNION ALL
SELECT 'addon_services', COUNT(*) FROM addon_services;

-- ==========================================================================
-- NOTES
-- ==========================================================================
-- 
-- 1. All tables explicitly include these Xata system fields:
--    - xata_id (TEXT, PRIMARY KEY, UNIQUE, NOT NULL) - Primary identifier
--    - xata_version (INTEGER, NOT NULL, DEFAULT 0) - Version for optimistic concurrency
--    - xata_createdat (TIMESTAMPTZ, NOT NULL, DEFAULT NOW()) - Creation timestamp
--    - xata_updatedat (TIMESTAMPTZ, NOT NULL, DEFAULT NOW()) - Last update timestamp
--
-- 2. xata_id serves as the primary key and is explicitly defined in all tables
--
-- 3. JSON fields are stored as JSON type in Xata and can be queried with JSON operators
--
-- 4. All tables include isActive fields for soft deletes instead of hard deletion
--
-- 5. displayOrder fields allow custom sorting in the application layer
--
-- 6. Enum-like fields use TEXT with application-level validation in FastAPI
--
-- 7. Business identifiers like planId and serviceId are NOT unique constraints
--    to avoid conflicts with Xata's primary key system
--
-- 8. This script includes comprehensive sample data to test your API endpoints
--
-- 9. After running this script, your FastAPI application should be able to
--    connect to Xata and perform CRUD operations on all content tables
--
-- ==========================================================================

-- Commit the transaction
COMMIT;

-- ==========================================================================
-- ROLLBACK INSTRUCTIONS
-- ==========================================================================
-- If you need to rollback the changes, run: ROLLBACK;
-- Note: This only works if you haven't committed yet
