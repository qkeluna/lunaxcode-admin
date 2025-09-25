#!/usr/bin/env python3
"""
FAQ Seed Data Script

This script populates the FAQ database with comprehensive seed data
covering various categories like pricing, support, features, etc.

Usage:
    python scripts/seed_faq_data.py
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.faq import FAQService
from app.models.faq import FAQCreate
from app.db.xata import get_xata_client

# Comprehensive seed data covering various FAQ categories
FAQ_SEED_DATA = [
    # Pricing & Plans
    {
        "question": "What are your pricing plans?",
        "answer": "We offer three main pricing tiers: Basic ($9.99/month), Professional ($29.99/month), and Enterprise ($99.99/month). Each plan includes different features and usage limits to suit various business needs.",
        "value": "pricing"
    },
    {
        "question": "Is there a free trial available?",
        "answer": "Yes! We offer a 14-day free trial for all our plans. No credit card required. You can cancel anytime during the trial period without any charges.",
        "value": "pricing"
    },
    {
        "question": "Can I upgrade or downgrade my plan?",
        "answer": "Absolutely! You can upgrade or downgrade your plan at any time from your account settings. Changes take effect immediately, and billing is prorated accordingly.",
        "value": "pricing"
    },
    {
        "question": "Do you offer annual billing discounts?",
        "answer": "Yes, we offer a 20% discount for annual billing on all plans. This can result in significant savings compared to monthly billing.",
        "value": "pricing"
    },

    # Account & Authentication
    {
        "question": "How do I reset my password?",
        "answer": "To reset your password, click the 'Forgot Password' link on the login page, enter your email address, and follow the instructions in the email we send you. The reset link is valid for 24 hours.",
        "value": "account"
    },
    {
        "question": "How do I change my email address?",
        "answer": "You can change your email address in your account settings. Go to Profile > Account Information > Email Address. You'll need to verify the new email address before the change takes effect.",
        "value": "account"
    },
    {
        "question": "Can I delete my account?",
        "answer": "Yes, you can delete your account from the Account Settings page. Please note that this action is irreversible and will permanently delete all your data, projects, and settings.",
        "value": "account"
    },

    # Features & Functionality
    {
        "question": "What integrations do you support?",
        "answer": "We support over 50 integrations including Slack, Discord, GitHub, GitLab, Jira, Trello, Google Workspace, Microsoft 365, Zapier, and many more. Check our integrations page for the complete list.",
        "value": "features"
    },
    {
        "question": "Is there an API available?",
        "answer": "Yes! We provide a comprehensive REST API with full documentation. You can access all core features programmatically, and we also offer webhooks for real-time notifications.",
        "value": "features"
    },
    {
        "question": "Do you support single sign-on (SSO)?",
        "answer": "SSO is available on our Professional and Enterprise plans. We support SAML 2.0, OAuth 2.0, and popular providers like Google, Microsoft Azure AD, and Okta.",
        "value": "features"
    },
    {
        "question": "Can I export my data?",
        "answer": "Yes, you can export all your data at any time. We support exports in JSON, CSV, and XML formats. Enterprise customers also have access to automated backup solutions.",
        "value": "features"
    },

    # Support & Technical
    {
        "question": "What support channels are available?",
        "answer": "We offer multiple support channels: email support (all plans), live chat (Professional and Enterprise), phone support (Enterprise only), and our comprehensive knowledge base available to everyone.",
        "value": "support"
    },
    {
        "question": "What are your support hours?",
        "answer": "Email support is available 24/7 with response times of 24 hours (Basic), 8 hours (Professional), and 2 hours (Enterprise). Live chat and phone support are available Monday-Friday, 9 AM to 6 PM EST.",
        "value": "support"
    },
    {
        "question": "How do I report a bug or request a feature?",
        "answer": "You can report bugs or request features through our support portal, email us at support@example.com, or use the feedback widget in the application. We track all requests and provide regular updates.",
        "value": "support"
    },

    # Security & Privacy
    {
        "question": "How do you protect my data?",
        "answer": "We use enterprise-grade security measures including AES-256 encryption at rest, TLS 1.3 for data in transit, regular security audits, and SOC 2 Type II compliance. All data is backed up daily with 99.9% uptime guarantee.",
        "value": "security"
    },
    {
        "question": "Where is my data stored?",
        "answer": "Your data is stored in secure, geographically distributed data centers. We offer data residency options for Enterprise customers and comply with GDPR, CCPA, and other privacy regulations.",
        "value": "security"
    },
    {
        "question": "Do you share my data with third parties?",
        "answer": "No, we never sell or share your personal data with third parties. We only share anonymized, aggregated usage statistics to improve our service. Read our detailed privacy policy for complete information.",
        "value": "security"
    },

    # Getting Started
    {
        "question": "How do I get started?",
        "answer": "Getting started is easy! Sign up for a free trial, complete the quick onboarding tutorial, and you'll be up and running in minutes. Our step-by-step guide will help you set up your first project.",
        "value": "getting-started"
    },
    {
        "question": "Do you provide training or onboarding?",
        "answer": "Yes! We offer comprehensive onboarding for all customers. Basic plan includes self-guided tutorials, Professional includes webinar training, and Enterprise includes dedicated onboarding specialist support.",
        "value": "getting-started"
    },

    # Billing & Payments
    {
        "question": "What payment methods do you accept?",
        "answer": "We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and for Enterprise customers, we also accept bank transfers and purchase orders.",
        "value": "billing"
    },
    {
        "question": "When will I be charged?",
        "answer": "For monthly plans, you're charged on the same date each month when you first subscribed. For annual plans, you're charged immediately and then annually on the same date. All charges appear on your statement as 'YourCompany Services'.",
        "value": "billing"
    }
]

async def seed_faq_data():
    """
    Seed the FAQ database with comprehensive test data
    """
    print("🌱 Starting FAQ Data Seeding Process")
    print(f"📊 Preparing to seed {len(FAQ_SEED_DATA)} FAQ records")
    
    try:
        # Get Xata client
        xata_client = get_xata_client()
        faq_service = FAQService(xata_client)
        
        # Track seeding statistics
        created_count = 0
        error_count = 0
        
        print("\n🚀 Creating FAQ records...")
        
        for i, faq_data in enumerate(FAQ_SEED_DATA, 1):
            try:
                # Create FAQ record
                faq_create = FAQCreate(**faq_data)
                result = await faq_service.create_faq(faq_create)
                
                created_count += 1
                print(f"✅ [{i:2d}/{len(FAQ_SEED_DATA)}] Created FAQ: {result.question[:50]}...")
                
                # Add small delay to avoid overwhelming the database
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                print(f"❌ [{i:2d}/{len(FAQ_SEED_DATA)}] Failed to create FAQ: {faq_data['question'][:50]}...")
                print(f"   Error: {str(e)}")
                continue
        
        print(f"\n📈 Seeding Summary:")
        print(f"   ✅ Successfully created: {created_count} FAQs")
        print(f"   ❌ Errors encountered: {error_count} FAQs")
        print(f"   📊 Success rate: {(created_count / len(FAQ_SEED_DATA)) * 100:.1f}%")
        
        # Verify the seeded data
        print(f"\n🔍 Verifying seeded data...")
        all_faqs = await faq_service.get_faqs()
        print(f"   📋 Total FAQs in database: {len(all_faqs)}")
        
        # Show category breakdown
        category_counts = {}
        for faq in all_faqs:
            category = faq.value or "uncategorized"
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print(f"   📊 Category breakdown:")
        for category, count in sorted(category_counts.items()):
            print(f"      {category}: {count} FAQs")
        
        if created_count > 0:
            print(f"\n🎉 FAQ seeding completed successfully!")
            print(f"🌐 You can now test the FAQ endpoints:")
            print(f"   GET  /api/faqs/                    - List all FAQs")
            print(f"   GET  /api/faqs/search?q=pricing    - Search for pricing FAQs")
            print(f"   GET  /api/faqs/by-value?value=support - Get support FAQs")
        else:
            print(f"\n⚠️  No FAQs were created. Please check the errors above.")
            
    except Exception as e:
        print(f"\n💥 Critical error during seeding: {str(e)}")
        return False
    
    return created_count > 0

def print_usage_examples():
    """Print usage examples for testing the seeded data"""
    print(f"\n📚 Usage Examples:")
    print(f"")
    print(f"# Test the seeded FAQ data")
    print(f"curl http://localhost:8000/api/faqs/")
    print(f"")
    print(f"# Search for pricing-related FAQs")
    print(f"curl 'http://localhost:8000/api/faqs/search?q=pricing'")
    print(f"")
    print(f"# Get all support FAQs")
    print(f"curl 'http://localhost:8000/api/faqs/by-value?value=support'")
    print(f"")
    print(f"# Get FAQs with pagination")
    print(f"curl 'http://localhost:8000/api/faqs/?limit=5'")
    print(f"")
    print(f"# Search for security-related content")
    print(f"curl 'http://localhost:8000/api/faqs/search?q=security'")

async def main():
    """Main function to run the seeding process"""
    print("=" * 60)
    print("🌱 FAQ Database Seeding Script")
    print("=" * 60)
    
    try:
        success = await seed_faq_data()
        
        if success:
            print_usage_examples()
            return 0
        else:
            print(f"\n❌ Seeding failed. Please check the errors above.")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Seeding interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    # Run the seeding process
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 