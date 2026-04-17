"""
PII Obfuscation Utilities for ServiceNow CMDB Data

This module provides deterministic obfuscation of personally identifiable information (PII)
using the Faker library. The same real ID will always generate the same fake identity,
ensuring consistency across multiple tool invocations.

Based on the obfuscation logic from scripts/obfuscate_kb_data.py
"""

from faker import Faker
import hashlib
from typing import Dict, Tuple


def generate_fake_identity(real_id: str) -> Tuple[str, str, str]:
    """
    Generate fake ID, name, and email deterministically from real ID.
    
    Uses MD5 hash of the real ID as a seed for Faker to ensure the same
    real ID always produces the same fake identity.
    
    Args:
        real_id: Original ID (e.g., "P067926", "FF0056")
        
    Returns:
        Tuple of (fake_id, fake_name, fake_email)
        
    Example:
        >>> fake_id, fake_name, fake_email = generate_fake_identity("P067926")
        >>> print(fake_id, fake_name, fake_email)
        ID12345 John Doe john.doe@pnc.com
    """
    # Handle empty IDs
    if not real_id or not real_id.strip():
        return '', '', ''
    
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


def obfuscate_person_fields(person_fields: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """
    Obfuscate all person fields using deterministic Faker generation.
    
    Args:
        person_fields: Dictionary with role keys (e.g., 'product_owner', 'rtb_asm', 
                      'it_app_owner', 'cio'). Each value is a dict with 'name', 'id', 'email'.
                      
    Returns:
        Dictionary with same structure but obfuscated values
        
    Example:
        >>> person_fields = {
        ...     'product_owner': {
        ...         'name': 'Harry Carr',
        ...         'id': 'P067926',
        ...         'email': 'harry.carr@pnc.com'
        ...     }
        ... }
        >>> obfuscated = obfuscate_person_fields(person_fields)
        >>> print(obfuscated['product_owner'])
        {'name': 'John Doe', 'id': 'ID12345', 'email': 'john.doe@pnc.com'}
    """
    obfuscated = {}
    
    for role, person_data in person_fields.items():
        real_id = person_data.get('id', '').strip()
        
        if real_id:  # Only obfuscate if ID exists
            fake_id, fake_name, fake_email = generate_fake_identity(real_id)
            obfuscated[role] = {
                'name': fake_name,
                'id': fake_id,
                'email': fake_email
            }
        else:  # Keep empty if no data
            obfuscated[role] = {
                'name': '',
                'id': '',
                'email': ''
            }
    
    return obfuscated


def obfuscate_single_person(name: str, user_id: str, email: str) -> Tuple[str, str, str]:
    """
    Obfuscate a single person's information.
    
    Convenience function for obfuscating individual person records.
    
    Args:
        name: Real name
        user_id: Real user ID
        email: Real email
        
    Returns:
        Tuple of (fake_name, fake_id, fake_email)
    """
    if not user_id or not user_id.strip():
        return '', '', ''
    
    return generate_fake_identity(user_id)


# Made with Bob