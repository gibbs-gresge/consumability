#!/usr/bin/env python3
"""
KB Data Obfuscation Script

This script obfuscates IDs, names, and emails in all files within the kb_data directory.
It uses deterministic generation based on the original ID to ensure consistency across all files.

Usage:
    python scripts/obfuscate_kb_data.py [--dry-run]

Options:
    --dry-run    Show what would be changed without actually modifying files
"""

import os
import re
import json
import hashlib
import shutil
import sys
from pathlib import Path
from typing import Dict, Set, Tuple
from faker import Faker


class KBDataObfuscator:
    """Handles obfuscation of KB data files with consistent fake identities."""
    
    def __init__(self, kb_data_dir: str = "data/kb_data"):
        self.kb_data_dir = Path(kb_data_dir)
        self.backup_dir = Path("data/kb_data_original")
        self.mapping_file = Path("data/obfuscation_mapping.json")
        self.person_records: Dict[str, Dict[str, str]] = {}
        self.mapping: Dict[str, Dict[str, str]] = {}
        
    def extract_person_records(self) -> Dict[str, Dict[str, str]]:
        """
        Extract all unique person records from kb_data files.
        
        Returns:
            Dictionary mapping real_id to {name, email}
        """
        print(f"📂 Scanning files in {self.kb_data_dir}...")
        
        # Pattern to match ID lines (various prefixes: PP, PK, PT, ZX, etc.)
        id_pattern = re.compile(r'- ID:\s*([A-Z]{2}\d{5})')
        name_pattern = re.compile(r'- Name:\s*(.+)')
        email_pattern = re.compile(r'- Email:\s*(.+)')
        
        person_records = {}
        files_processed = 0
        
        # Process all .txt files in kb_data directory
        for filepath in sorted(self.kb_data_dir.glob("*.txt")):
            files_processed += 1
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all person records in the file
            lines = content.split('\n')
            current_name = None
            current_id = None
            current_email = None
            
            for line in lines:
                # Check for name
                name_match = name_pattern.search(line)
                if name_match:
                    current_name = name_match.group(1).strip()
                
                # Check for ID
                id_match = id_pattern.search(line)
                if id_match:
                    current_id = id_match.group(1).strip()
                
                # Check for email
                email_match = email_pattern.search(line)
                if email_match:
                    current_email = email_match.group(1).strip()
                
                # If we have all three, store the record
                if current_name and current_id and current_email:
                    if current_id not in person_records:
                        person_records[current_id] = {
                            'name': current_name,
                            'email': current_email
                        }
                    # Reset for next person
                    current_name = None
                    current_id = None
                    current_email = None
        
        print(f"✅ Processed {files_processed} files")
        print(f"✅ Found {len(person_records)} unique person records")
        
        self.person_records = person_records
        return person_records
    
    def generate_fake_identity(self, real_id: str) -> Tuple[str, str, str]:
        """
        Generate fake ID, name, and email deterministically from real ID.
        
        Args:
            real_id: Original ID (e.g., "REDACTED")
            
        Returns:
            Tuple of (fake_id, fake_name, fake_email)
        """
        # Create deterministic seed from real ID
        seed = int(hashlib.md5(real_id.encode()).hexdigest(), 16) % (10**8)
        
        # Initialize Faker with seed for consistency
        fake = Faker()
        Faker.seed(seed)
        
        # Generate fake ID (ID + 5 digits)
        fake_id_number = seed % 100000  # Ensures 0-99999 range
        fake_id = f"ID{fake_id_number:05d}"
        
        # Generate fake name
        fake_name = fake.name()
        
        # Generate fake email from name (lowercase, replace spaces with dots)
        email_name = fake_name.lower().replace(' ', '.').replace("'", "")
        fake_email = f"{email_name}@pnc.com"
        
        return fake_id, fake_name, fake_email
    
    def create_mapping(self) -> Dict[str, Dict[str, str]]:
        """
        Create mapping from real IDs to fake identities.
        
        Returns:
            Dictionary mapping real_id to fake identity data
        """
        print("\n🎭 Generating fake identities...")
        
        mapping = {}
        
        for real_id, person_data in self.person_records.items():
            fake_id, fake_name, fake_email = self.generate_fake_identity(real_id)
            
            mapping[real_id] = {
                'real_id': real_id,
                'real_name': person_data['name'],
                'real_email': person_data['email'],
                'fake_id': fake_id,
                'fake_name': fake_name,
                'fake_email': fake_email
            }
        
        print(f"✅ Generated {len(mapping)} fake identities")
        
        self.mapping = mapping
        return mapping
    
    def save_mapping(self):
        """Save the mapping to a JSON file."""
        print(f"\n💾 Saving mapping to {self.mapping_file}...")
        
        # Ensure data directory exists
        self.mapping_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.mapping, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Mapping saved successfully")
    
    def backup_files(self):
        """Create backup of original files."""
        if self.backup_dir.exists():
            print(f"\n⚠️  Backup directory already exists: {self.backup_dir}")
            response = input("Do you want to overwrite it? (yes/no): ").strip().lower()
            if response != 'yes':
                print("❌ Backup cancelled. Exiting.")
                sys.exit(1)
            shutil.rmtree(self.backup_dir)
        
        print(f"\n💾 Creating backup at {self.backup_dir}...")
        shutil.copytree(self.kb_data_dir, self.backup_dir)
        print(f"✅ Backup created successfully")
    
    def obfuscate_file(self, filepath: Path, dry_run: bool = False) -> int:
        """
        Obfuscate a single file by replacing real data with fake data.
        
        Args:
            filepath: Path to the file to obfuscate
            dry_run: If True, don't actually modify the file
            
        Returns:
            Number of replacements made
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements = 0
        
        # Replace each person's data
        for real_id, data in self.mapping.items():
            # Replace ID
            id_pattern = re.compile(rf'- ID:\s*{re.escape(real_id)}')
            if id_pattern.search(content):
                content = id_pattern.sub(f"- ID: {data['fake_id']}", content)
                replacements += 1
            
            # Replace name (be careful to match exact name)
            name_pattern = re.compile(rf'- Name:\s*{re.escape(data["real_name"])}')
            if name_pattern.search(content):
                content = name_pattern.sub(f"- Name: {data['fake_name']}", content)
                replacements += 1
            
            # Replace email
            email_pattern = re.compile(rf'- Email:\s*{re.escape(data["real_email"])}')
            if email_pattern.search(content):
                content = email_pattern.sub(f"- Email: {data['fake_email']}", content)
                replacements += 1
        
        # Write back if not dry run and content changed
        if not dry_run and content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return replacements
    
    def obfuscate_all_files(self, dry_run: bool = False):
        """
        Obfuscate all files in the kb_data directory.
        
        Args:
            dry_run: If True, show what would be changed without modifying files
        """
        mode = "DRY RUN" if dry_run else "LIVE"
        print(f"\n🔄 Obfuscating files ({mode})...")
        
        total_replacements = 0
        files_modified = 0
        
        for filepath in sorted(self.kb_data_dir.glob("*.txt")):
            replacements = self.obfuscate_file(filepath, dry_run)
            if replacements > 0:
                files_modified += 1
                total_replacements += replacements
                status = "would be modified" if dry_run else "modified"
                print(f"  ✓ {filepath.name}: {replacements} replacements ({status})")
        
        print(f"\n✅ {files_modified} files {'would be' if dry_run else ''} modified")
        print(f"✅ {total_replacements} total replacements {'would be' if dry_run else ''} made")
    
    def verify_consistency(self) -> bool:
        """
        Verify that the same real ID maps to the same fake identity across all files.
        
        Returns:
            True if consistent, False otherwise
        """
        print("\n🔍 Verifying consistency...")
        
        # Track what fake data we see for each real ID
        id_to_fake_data: Dict[str, Set[Tuple[str, str, str]]] = {}
        
        for filepath in sorted(self.kb_data_dir.glob("*.txt")):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            current_name = None
            current_id = None
            current_email = None
            
            for line in lines:
                if '- Name:' in line:
                    current_name = line.split('- Name:')[1].strip()
                if '- ID:' in line:
                    current_id = line.split('- ID:')[1].strip()
                if '- Email:' in line:
                    current_email = line.split('- Email:')[1].strip()
                
                if current_name and current_id and current_email:
                    # Find the real ID that maps to this fake ID
                    real_id = None
                    for rid, data in self.mapping.items():
                        if data['fake_id'] == current_id:
                            real_id = rid
                            break
                    
                    if real_id:
                        if real_id not in id_to_fake_data:
                            id_to_fake_data[real_id] = set()
                        id_to_fake_data[real_id].add((current_id, current_name, current_email))
                    
                    current_name = None
                    current_id = None
                    current_email = None
        
        # Check for inconsistencies
        inconsistencies = []
        for real_id, fake_data_set in id_to_fake_data.items():
            if len(fake_data_set) > 1:
                inconsistencies.append((real_id, fake_data_set))
        
        if inconsistencies:
            print("❌ Inconsistencies found:")
            for real_id, fake_data_set in inconsistencies:
                print(f"  Real ID {real_id} maps to multiple fake identities:")
                for fake_id, fake_name, fake_email in fake_data_set:
                    print(f"    - {fake_id}, {fake_name}, {fake_email}")
            return False
        
        print("✅ All files are consistent!")
        print(f"✅ Verified {len(id_to_fake_data)} unique person records")
        return True
    
    def run(self, dry_run: bool = False):
        """
        Run the complete obfuscation process.
        
        Args:
            dry_run: If True, show what would be changed without modifying files
        """
        print("=" * 70)
        print("KB DATA OBFUSCATION TOOL")
        print("=" * 70)
        
        # Step 1: Extract person records
        self.extract_person_records()
        
        # Step 2: Generate fake identities
        self.create_mapping()
        
        # Step 3: Save mapping
        self.save_mapping()
        
        if not dry_run:
            # Step 4: Backup files
            self.backup_files()
            
            # Step 5: Obfuscate files
            self.obfuscate_all_files(dry_run=False)
            
            # Step 6: Verify consistency
            self.verify_consistency()
        else:
            # Dry run: just show what would happen
            self.obfuscate_all_files(dry_run=True)
        
        print("\n" + "=" * 70)
        if dry_run:
            print("DRY RUN COMPLETE - No files were modified")
        else:
            print("OBFUSCATION COMPLETE!")
            print(f"Original files backed up to: {self.backup_dir}")
            print(f"Mapping saved to: {self.mapping_file}")
        print("=" * 70)


def main():
    """Main entry point."""
    dry_run = '--dry-run' in sys.argv
    
    obfuscator = KBDataObfuscator()
    obfuscator.run(dry_run=dry_run)


if __name__ == "__main__":
    main()

# Made with Bob
