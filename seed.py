#!/usr/bin/env python3
"""
Simple seed script runner for Lunaxcode CMS.
Run this script to populate your database with realistic sample data.
"""

import asyncio
import sys
from scripts.seed_data import main

if __name__ == "__main__":
    print("🌱 Lunaxcode CMS Database Seeder")
    print("=" * 40)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Seeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        sys.exit(1)
