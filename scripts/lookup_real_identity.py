#!/usr/bin/env python3
"""
Real Identity Lookup Tool

This script allows you to look up real identities from fake (obfuscated) data.
It reads the obfuscation mapping file and provides various lookup methods.

Usage:
    # Lookup by fake ID
    python scripts/lookup_real_identity.py --fake-id ID12345
    
    # Lookup by fake name
    python scripts/lookup_real_identity.py --fake-name "Robert Anderson"
    
    # Lookup by fake email
    python scripts/lookup_real_identity.py --fake-email robert.anderson@pnc.com
    
    # Lookup by real ID
    python scripts/lookup_real_identity.py --real-id REDACTED
    
    # Interactive mode
    python scripts/lookup_real_identity.py --interactive
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional


class IdentityLookup:
    """Handles lookup of real identities from obfuscated data."""
    
    def __init__(self, mapping_file: str = "data/obfuscation_mapping.json"):
        self.mapping_file = Path(mapping_file)
        self.mapping: Dict[str, Dict[str, str]] = {}
        self.load_mapping()
    
    def load_mapping(self):
        """Load the obfuscation mapping from JSON file."""
        if not self.mapping_file.exists():
            print(f"❌ Error: Mapping file not found: {self.mapping_file}")
            print("   Please run obfuscate_kb_data.py first to generate the mapping.")
            sys.exit(1)
        
        with open(self.mapping_file, 'r', encoding='utf-8') as f:
            self.mapping = json.load(f)
        
        print(f"✅ Loaded mapping with {len(self.mapping)} records\n")
    
    def lookup_by_fake_id(self, fake_id: str) -> Optional[Dict[str, str]]:
        """
        Find real identity by fake ID.
        
        Args:
            fake_id: Fake ID to search for (e.g., "ID12345")
            
        Returns:
            Dictionary with real identity data or None if not found
        """
        for real_id, data in self.mapping.items():
            if data['fake_id'] == fake_id:
                return data
        return None
    
    def lookup_by_fake_name(self, fake_name: str) -> Optional[Dict[str, str]]:
        """
        Find real identity by fake name.
        
        Args:
            fake_name: Fake name to search for (e.g., "Robert Anderson")
            
        Returns:
            Dictionary with real identity data or None if not found
        """
        for real_id, data in self.mapping.items():
            if data['fake_name'].lower() == fake_name.lower():
                return data
        return None
    
    def lookup_by_fake_email(self, fake_email: str) -> Optional[Dict[str, str]]:
        """
        Find real identity by fake email.
        
        Args:
            fake_email: Fake email to search for (e.g., "robert.anderson@pnc.com")
            
        Returns:
            Dictionary with real identity data or None if not found
        """
        for real_id, data in self.mapping.items():
            if data['fake_email'].lower() == fake_email.lower():
                return data
        return None
    
    def lookup_by_real_id(self, real_id: str) -> Optional[Dict[str, str]]:
        """
        Find fake identity by real ID.
        
        Args:
            real_id: Real ID to search for (e.g., "REDACTED")
            
        Returns:
            Dictionary with fake identity data or None if not found
        """
        return self.mapping.get(real_id)
    
    def display_result(self, data: Optional[Dict[str, str]], lookup_type: str):
        """
        Display lookup result in a formatted way.
        
        Args:
            data: Identity data dictionary or None
            lookup_type: Description of what was looked up
        """
        if data is None:
            print(f"❌ No match found for {lookup_type}")
            return
        
        print("=" * 70)
        print(f"LOOKUP RESULT: {lookup_type}")
        print("=" * 70)
        print("\n📋 REAL IDENTITY:")
        print(f"   ID:    {data['real_id']}")
        print(f"   Name:  {data['real_name']}")
        print(f"   Email: {data['real_email']}")
        print("\n🎭 FAKE IDENTITY:")
        print(f"   ID:    {data['fake_id']}")
        print(f"   Name:  {data['fake_name']}")
        print(f"   Email: {data['fake_email']}")
        print("=" * 70)
    
    def interactive_mode(self):
        """Run interactive lookup mode."""
        print("=" * 70)
        print("INTERACTIVE IDENTITY LOOKUP")
        print("=" * 70)
        print("\nAvailable lookup types:")
        print("  1. Lookup by fake ID")
        print("  2. Lookup by fake name")
        print("  3. Lookup by fake email")
        print("  4. Lookup by real ID")
        print("  5. List all mappings")
        print("  6. Exit")
        
        while True:
            print("\n" + "-" * 70)
            choice = input("Enter choice (1-6): ").strip()
            
            if choice == '1':
                fake_id = input("Enter fake ID (e.g., ID12345): ").strip()
                result = self.lookup_by_fake_id(fake_id)
                self.display_result(result, f"Fake ID: {fake_id}")
            
            elif choice == '2':
                fake_name = input("Enter fake name (e.g., Robert Anderson): ").strip()
                result = self.lookup_by_fake_name(fake_name)
                self.display_result(result, f"Fake Name: {fake_name}")
            
            elif choice == '3':
                fake_email = input("Enter fake email (e.g., robert.anderson@pnc.com): ").strip()
                result = self.lookup_by_fake_email(fake_email)
                self.display_result(result, f"Fake Email: {fake_email}")
            
            elif choice == '4':
                real_id = input("Enter real ID (e.g., REDACTED): ").strip()
                result = self.lookup_by_real_id(real_id)
                self.display_result(result, f"Real ID: {real_id}")
            
            elif choice == '5':
                self.list_all_mappings()
            
            elif choice == '6':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-6.")
    
    def list_all_mappings(self):
        """Display all mappings in a table format."""
        print("\n" + "=" * 70)
        print("ALL IDENTITY MAPPINGS")
        print("=" * 70)
        print(f"\n{'Real ID':<10} {'Real Name':<25} {'Fake ID':<10} {'Fake Name':<25}")
        print("-" * 70)
        
        for real_id, data in sorted(self.mapping.items()):
            real_name = data['real_name'][:24] if len(data['real_name']) > 24 else data['real_name']
            fake_name = data['fake_name'][:24] if len(data['fake_name']) > 24 else data['fake_name']
            print(f"{real_id:<10} {real_name:<25} {data['fake_id']:<10} {fake_name:<25}")
        
        print(f"\nTotal: {len(self.mapping)} mappings")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Lookup real identities from obfuscated data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --fake-id ID12345
  %(prog)s --fake-name "Robert Anderson"
  %(prog)s --fake-email robert.anderson@pnc.com
  %(prog)s --real-id REDACTED
  %(prog)s --interactive
        """
    )
    
    parser.add_argument('--fake-id', help='Lookup by fake ID')
    parser.add_argument('--fake-name', help='Lookup by fake name')
    parser.add_argument('--fake-email', help='Lookup by fake email')
    parser.add_argument('--real-id', help='Lookup by real ID')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--list-all', '-l', action='store_true',
                       help='List all mappings')
    
    args = parser.parse_args()
    
    # Create lookup instance
    lookup = IdentityLookup()
    
    # Handle different lookup modes
    if args.interactive:
        lookup.interactive_mode()
    elif args.list_all:
        lookup.list_all_mappings()
    elif args.fake_id:
        result = lookup.lookup_by_fake_id(args.fake_id)
        lookup.display_result(result, f"Fake ID: {args.fake_id}")
    elif args.fake_name:
        result = lookup.lookup_by_fake_name(args.fake_name)
        lookup.display_result(result, f"Fake Name: {args.fake_name}")
    elif args.fake_email:
        result = lookup.lookup_by_fake_email(args.fake_email)
        lookup.display_result(result, f"Fake Email: {args.fake_email}")
    elif args.real_id:
        result = lookup.lookup_by_real_id(args.real_id)
        lookup.display_result(result, f"Real ID: {args.real_id}")
    else:
        parser.print_help()
        print("\n💡 Tip: Use --interactive for an interactive lookup session")


if __name__ == "__main__":
    main()

# Made with Bob
