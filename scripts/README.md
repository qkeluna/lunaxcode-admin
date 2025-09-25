# Database Seeding Scripts

This directory contains scripts to populate your Lunaxcode CMS database with realistic sample data.

## Quick Start

Run the seed script from the project root:

```bash
python seed.py
```

## What Gets Seeded

The script will populate all your content tables with 10 realistic records each:

### 📋 **Pricing Plans** (10 records)
- Landing Page Basic & Premium
- Web App Starter & Professional  
- Mobile App Basic & Advanced
- E-commerce Basic & Professional
- Development Consulting
- Website Maintenance

### ⭐ **Features** (10 records)
- Lightning Fast Development
- Mobile-First Design
- SEO Optimized
- Secure & Reliable
- Custom Integrations
- 24/7 Support
- And more...

### 🔄 **Process Steps** (10 records)
- Discovery & Planning
- Design & Prototyping
- Development
- Testing & QA
- Deployment & Launch
- Training & Documentation
- And more...

### 🎯 **Hero Sections** (3 records)
- Multiple headline variations
- Different CTA combinations
- Ready-to-use copy

### 💬 **Testimonials** (10 records)
- Real-sounding client reviews
- Various project types
- Professional avatars
- 5-star ratings

### 📞 **Contact Info** (10 records)
- Business email & support
- Phone & WhatsApp
- Social media links
- Business address

### ❓ **FAQs** (10 records)
- Common questions about pricing
- Process explanations
- Technical information
- General inquiries

### ⚙️ **Site Settings** (10 records)
- Site configuration
- Contact information
- Social media links
- Analytics settings

### 🛠️ **Addon Services** (10 records)
- SEO Optimization
- Logo Design
- Content Writing
- SSL Certificate
- Email Setup
- And more...

## Features

- **🧹 Clean Slate**: Removes all existing data first
- **📊 Realistic Data**: Professional, Philippines-focused content
- **🎨 Complete**: Covers all your content models
- **🔒 Safe**: Uses proper validation and error handling
- **📝 Detailed**: Comprehensive logging throughout process

## Running the Script

1. **Make sure your API is running and connected to Xata**
2. **Set your environment variables** (XATA_API_KEY, XATA_DATABASE_URL)
3. **Run from project root**:
   ```bash
   python seed.py
   ```

## Sample Output

```
🌱 Lunaxcode CMS Database Seeder
========================================
🌱 Starting database seeding process...
✅ Connected to Xata database

🧹 Clearing existing data...
✅ Cleared table: pricing_plans
✅ Cleared table: features
...

📝 Seeding new data...
✅ Seeded 10 pricing plans
✅ Seeded 10 features
✅ Seeded 10 process steps
...

🎉 Database seeding completed successfully!
🔌 Database connection closed
```

## Customization

You can modify `scripts/seed_data.py` to:
- Add more records
- Change the sample data
- Adjust pricing for your market
- Update contact information
- Modify business details

## Troubleshooting

If you encounter issues:

1. **Database Connection**: Ensure your Xata credentials are correct
2. **Table Structure**: Verify your database schema matches the models
3. **Permissions**: Make sure your API key has write permissions
4. **Network**: Check your internet connection to Xata

## Reset Data

To clear all data and reseed:
```bash
python seed.py
```
The script automatically clears existing data before seeding new records.
