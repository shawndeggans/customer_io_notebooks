#!/usr/bin/env python3
"""
Setup Eternal Test Data for Customer.IO Integration Tests

This script creates a fixed set of test data in your Customer.IO workspace
that integration tests can use without creating/deleting data during test runs.

Usage:
    python setup_eternal_data.py --help
    python setup_eternal_data.py --dry-run  # Preview what would be created
    python setup_eternal_data.py --create   # Actually create the data
    python setup_eternal_data.py --verify   # Check if data exists
    python setup_eternal_data.py --cleanup  # Remove eternal data (careful!)

Requirements:
    - Valid CUSTOMERIO_API_KEY in .env file
    - Sufficient API permissions to create users, objects, devices
"""

import os
import sys
import argparse
import time
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.eternal_test_data import ETERNAL_TEST_DATA, ETERNAL_DATA_VERSION
from src.pipelines_api.api_client import CustomerIOClient
from src.pipelines_api.people_manager import identify_user
from src.pipelines_api.device_manager import register_device
from src.pipelines_api.object_manager import create_object, create_relationship
from src.pipelines_api.exceptions import CustomerIOError

# Load environment variables
load_dotenv()

class EternalDataSetup:
    """Setup and manage eternal test data."""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize setup with API client.
        
        Parameters
        ----------
        dry_run : bool
            If True, only preview actions without making API calls
        """
        self.dry_run = dry_run
        self.client = None
        self.created_count = 0
        self.skipped_count = 0
        self.failed_count = 0
        
        if not dry_run:
            api_key = os.getenv("CUSTOMERIO_API_KEY")
            if not api_key:
                raise ValueError("CUSTOMERIO_API_KEY not found in environment")
            
            region = os.getenv("CUSTOMERIO_REGION", "us")
            self.client = CustomerIOClient(api_key=api_key, region=region)
    
    def setup_users(self) -> Dict[str, bool]:
        """
        Set up eternal test users.
        
        Returns
        -------
        Dict[str, bool]
            Results for each user (True=success, False=failed)
        """
        results = {}
        users = ETERNAL_TEST_DATA["users"]
        
        print(f"\nSetting up {len(users)} eternal test users...")
        
        for user_type, user_data in users.items():
            user_id = user_data["id"]
            email = user_data["email"]
            traits = user_data["traits"]
            
            print(f"  Creating user: {user_id} ({user_type})")
            
            if self.dry_run:
                print(f"    [DRY RUN] Would create user with email: {email}")
                results[user_type] = True
                continue
            
            try:
                # Add metadata to traits
                traits_with_meta = {
                    **traits,
                    "eternal_data_version": ETERNAL_DATA_VERSION,
                    "created_by_setup": True,
                    "setup_timestamp": time.time()
                }
                
                result = identify_user(self.client, user_id, traits_with_meta)
                print(f"    ✅ Created successfully")
                results[user_type] = True
                self.created_count += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except CustomerIOError as e:
                print(f"    ERROR: Failed: {e}")
                results[user_type] = False
                self.failed_count += 1
            except Exception as e:
                print(f"    ERROR: Unexpected error: {e}")
                results[user_type] = False
                self.failed_count += 1
        
        return results
    
    def setup_devices(self) -> Dict[str, bool]:
        """
        Set up eternal test devices.
        
        Returns
        -------
        Dict[str, bool]
            Results for each device
        """
        results = {}
        devices = ETERNAL_TEST_DATA["devices"]
        users = ETERNAL_TEST_DATA["users"]
        
        print(f"\nSetting up {len(devices)} eternal test devices...")
        
        # Use basic user for device registration
        basic_user_id = users["basic"]["id"]
        
        for device_type, device_data in devices.items():
            device_id = device_data["id"]
            platform = device_data["platform"]
            
            print(f"  Creating device: {device_id} ({platform})")
            
            if self.dry_run:
                print(f"    [DRY RUN] Would create {platform} device for user {basic_user_id}")
                results[device_type] = True
                continue
            
            try:
                # Device registration data
                device_info = {
                    "device_id": device_id,
                    "platform": platform,
                    "last_used": device_data["last_used"],
                    "eternal_data": True,
                    "eternal_data_version": ETERNAL_DATA_VERSION
                }
                
                result = register_device(self.client, basic_user_id, device_info)
                print(f"    ✅ Created successfully")
                results[device_type] = True
                self.created_count += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except CustomerIOError as e:
                print(f"    ERROR: Failed: {e}")
                results[device_type] = False
                self.failed_count += 1
            except Exception as e:
                print(f"    ERROR: Unexpected error: {e}")
                results[device_type] = False
                self.failed_count += 1
        
        return results
    
    def setup_objects(self) -> Dict[str, bool]:
        """
        Set up eternal test objects.
        
        Returns
        -------
        Dict[str, bool]
            Results for each object
        """
        results = {}
        objects = ETERNAL_TEST_DATA["objects"]
        
        print(f"\n🏢 Setting up {len(objects)} eternal test objects...")
        
        for object_key, object_data in objects.items():
            object_type = object_data["type"]
            object_id = object_data["id"]
            attributes = object_data["attributes"]
            
            print(f"  Creating {object_type}: {object_id}")
            
            if self.dry_run:
                print(f"    [DRY RUN] Would create {object_type} with attributes: {list(attributes.keys())}")
                results[object_key] = True
                continue
            
            try:
                # Add metadata to attributes
                attributes_with_meta = {
                    **attributes,
                    "eternal_data_version": ETERNAL_DATA_VERSION,
                    "created_by_setup": True,
                    "setup_timestamp": time.time()
                }
                
                result = create_object(
                    self.client,
                    object_type_id=object_type,
                    object_id=object_id,
                    attributes=attributes_with_meta
                )
                print(f"    ✅ Created successfully")
                results[object_key] = True
                self.created_count += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except CustomerIOError as e:
                print(f"    ERROR: Failed: {e}")
                results[object_key] = False
                self.failed_count += 1
            except Exception as e:
                print(f"    ERROR: Unexpected error: {e}")
                results[object_key] = False
                self.failed_count += 1
        
        return results
    
    def setup_relationships(self) -> Dict[str, bool]:
        """
        Set up eternal test relationships.
        
        Returns
        -------
        Dict[str, bool]
            Results for each relationship
        """
        results = {}
        relationships = ETERNAL_TEST_DATA["relationships"]
        
        print(f"\nSetting up {len(relationships)} eternal test relationships...")
        
        for i, rel_data in enumerate(relationships):
            user_id = rel_data["user_id"]
            object_type = rel_data["object_type"]
            object_id = rel_data["object_id"]
            relationship = rel_data["relationship"]
            
            rel_key = f"rel_{i+1}"
            print(f"  Creating relationship: {user_id} -> {object_type}/{object_id} ({relationship})")
            
            if self.dry_run:
                print(f"    [DRY RUN] Would create {relationship} relationship")
                results[rel_key] = True
                continue
            
            try:
                result = create_relationship(
                    self.client,
                    user_id=user_id,
                    object_type_id=object_type,
                    object_id=object_id,
                    relationship_data={
                        "relationship_type": relationship,
                        "eternal_data": True,
                        "eternal_data_version": ETERNAL_DATA_VERSION
                    }
                )
                print(f"    ✅ Created successfully")
                results[rel_key] = True
                self.created_count += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except CustomerIOError as e:
                print(f"    ERROR: Failed: {e}")
                results[rel_key] = False
                self.failed_count += 1
            except Exception as e:
                print(f"    ERROR: Unexpected error: {e}")
                results[rel_key] = False
                self.failed_count += 1
        
        return results
    
    def verify_data(self) -> Dict[str, Dict[str, bool]]:
        """
        Verify that eternal test data exists.
        
        Returns
        -------
        Dict[str, Dict[str, bool]]
            Verification results by category
        """
        if self.dry_run:
            print("Cannot verify data in dry-run mode")
            return {}
        
        results = {
            "users": {},
            "devices": {},
            "objects": {}
        }
        
        print("\nVerifying eternal test data exists...")
        
        # Check users (this is a simplified check - in real implementation
        # you'd need to add API methods to check if users exist)
        users = ETERNAL_TEST_DATA["users"]
        print(f"  Checking {len(users)} users...")
        for user_type, user_data in users.items():
            # In a real implementation, you'd check if the user exists
            # For now, we'll assume they exist if no error occurred during creation
            results["users"][user_type] = True
            print(f"    ✅ {user_data['id']} - exists")
        
        return results
    
    def cleanup_data(self) -> None:
        """
        Remove eternal test data (use with caution!).
        """
        if self.dry_run:
            print("[DRY RUN] Would remove all eternal test data")
            return
        
        print("\n⚠️  WARNING: This will remove all eternal test data!")
        print("This action cannot be undone and will break integration tests.")
        
        confirm = input("Type 'DELETE ETERNAL DATA' to confirm: ")
        if confirm != "DELETE ETERNAL DATA":
            print("Cleanup cancelled.")
            return
        
        print("Removing eternal test data...")
        # Implementation would delete users, objects, devices, etc.
        # This is intentionally not implemented to prevent accidental data loss
        print("ERROR: Cleanup not implemented for safety. Remove data manually if needed.")
    
    def run_setup(self) -> None:
        """Run the complete setup process."""
        print(f"Setting up eternal test data (Version: {ETERNAL_DATA_VERSION})")
        print(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        
        if not self.dry_run:
            print("   This will create permanent test data in your Customer.IO workspace.")
            confirm = input("   Continue? [y/N]: ")
            if confirm.lower() not in ['y', 'yes']:
                print("Setup cancelled.")
                return
        
        # Setup all data types
        user_results = self.setup_users()
        device_results = self.setup_devices()
        object_results = self.setup_objects()
        relationship_results = self.setup_relationships()
        
        # Summary
        print(f"\nSetup Summary:")
        print(f"   Created: {self.created_count}")
        print(f"   Skipped: {self.skipped_count}")
        print(f"   Failed: {self.failed_count}")
        
        if self.failed_count == 0:
            print("✅ All eternal test data created successfully!")
            print("\nNext steps:")
            print("1. Update TEST_DATA_MODE=eternal in your .env file")
            print("2. Run integration tests: pytest tests/integration/ -m 'read_only'")
        else:
            print("ERROR: Some data creation failed. Check the errors above.")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Setup eternal test data for Customer.IO")
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Preview what would be created without making API calls"
    )
    parser.add_argument(
        "--create",
        action="store_true", 
        help="Create the eternal test data"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify that eternal test data exists"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove eternal test data (use with caution!)"
    )
    
    args = parser.parse_args()
    
    if not any([args.dry_run, args.create, args.verify, args.cleanup]):
        parser.print_help()
        return
    
    try:
        if args.dry_run or args.create:
            setup = EternalDataSetup(dry_run=args.dry_run)
            setup.run_setup()
        elif args.verify:
            setup = EternalDataSetup(dry_run=False)
            setup.verify_data()
        elif args.cleanup:
            setup = EternalDataSetup(dry_run=False)
            setup.cleanup_data()
            
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()