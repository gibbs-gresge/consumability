"""
Prepare Victor Apps data for optimal knowledge base chunking
This script converts the Excel file to individual JSON documents (one per application)
to ensure precise chunking control - one application per chunk.
"""

import pandas as pd
import json
import os
from pathlib import Path

def prepare_data_for_kb(excel_file: str, output_dir: str = "kb_data"):
    """
    Convert Victor Apps Excel to individual JSON files for precise chunking.
    Each application becomes a separate document.
    
    Args:
        excel_file: Path to Victor Apps Excel file
        output_dir: Directory to store individual JSON files
    """
    print(f"Reading Excel file: {excel_file}")
    
    # Read the Excel file
    df = pd.read_excel(excel_file, sheet_name='VictorApps')
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Process each row as a separate document
    documents_created = 0
    
    for idx, row in df.iterrows():
        # Create a structured document for each application
        app_code = str(row['APP_CODE']).strip()
        
        # Build the document content
        doc = {
            "application_name": str(row['NAME']),
            "app_code": app_code,
            "description": str(row['DESCRIPTION']),
            "product_owner": {
                "name": str(row['OWNED_BY']),
                "id": str(row['OWNED_BY_ID']),
                "email": str(row['OWNED_BY_EMAIL'])
            },
            "rtb_asm": {
                "name": str(row['RTB_ASM']),
                "id": str(row['RTB_ASM_ID']),
                "email": str(row['RTB_ASM_EMAIL']),
                "role": "RUN THE BANK APPLICATION SYSTEM MANAGER - Sev1 Response Personnel"
            },
            "ctb_asm": {
                "name": str(row['CTB_ASM']),
                "id": str(row['CTB_ASM_ID']),
                "email": str(row['CTB_ASM_EMAIL']),
                "role": "CHANGE THE BANK ASM - Tech Leader for Changes, New Versions, Bug Fixes"
            },
            "cio": {
                "name": str(row['CIO']),
                "id": str(row['CIO_ID']),
                "email": str(row['CIO_EMAIL'])
            },
            "last_updated": str(row['LOAD_DATE'])
        }
        
        # Create a text representation for better search
        text_content = f"""
APPLICATION: {doc['application_name']}
APP_CODE: {app_code}

DESCRIPTION: {doc['description']}

PRODUCT OWNER (OWNED_BY):
- Name: {doc['product_owner']['name']}
- ID: {doc['product_owner']['id']}
- Email: {doc['product_owner']['email']}

RTB_ASM (Run The Bank - Sev1 Response Personnel):
- Name: {doc['rtb_asm']['name']}
- ID: {doc['rtb_asm']['id']}
- Email: {doc['rtb_asm']['email']}
- Role: {doc['rtb_asm']['role']}

CTB_ASM (Change The Bank - Tech Leader):
- Name: {doc['ctb_asm']['name']}
- ID: {doc['ctb_asm']['id']}
- Email: {doc['ctb_asm']['email']}
- Role: {doc['ctb_asm']['role']}

CIO:
- Name: {doc['cio']['name']}
- ID: {doc['cio']['id']}
- Email: {doc['cio']['email']}

LAST UPDATED: {doc['last_updated']}
        """.strip()
        
        # Save as individual text file (one per application)
        filename = f"{app_code}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        documents_created += 1
        
        if documents_created % 50 == 0:
            print(f"  Processed {documents_created} applications...")
    
    print(f"\n✓ Created {documents_created} individual documents in {output_dir}/")
    print(f"  Each document represents one application (one chunk)")
    
    return documents_created

def create_consolidated_file(output_dir: str = "kb_data", output_file: str = "victor_apps_consolidated.txt"):
    """
    Create a single consolidated file with clear separators for chunking.
    Alternative approach if individual files don't work.
    """
    print(f"\nCreating consolidated file: {output_file}")
    
    files = sorted([f for f in os.listdir(output_dir) if f.endswith('.txt')])
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for idx, filename in enumerate(files):
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as infile:
                content = infile.read()
                
                # Add clear separator between applications
                outfile.write(content)
                outfile.write("\n\n" + "="*80 + "\n\n")
    
    print(f"✓ Consolidated file created: {output_file}")
    print(f"  Contains {len(files)} applications with clear separators")

if __name__ == "__main__":
    # Prepare data
    excel_file = "data/source/Victor Apps (Products and Services) - Updated.xlsx"
    output_dir = "data/kb_data"
    
    if not os.path.exists(excel_file):
        print(f"Error: {excel_file} not found")
        print("Please ensure the Victor Apps Excel file is in data/source/ directory")
        exit(1)
    
    # Create individual files (best for chunking control)
    num_docs = prepare_data_for_kb(excel_file, output_dir)
    
    # Also create consolidated file as backup
    create_consolidated_file(output_dir, "data/source/victor_apps_consolidated.txt")
    
    print("\n" + "="*80)
    print("DATA PREPARATION COMPLETE")
    print("="*80)
    print("\nYou can now use either:")
    print("1. Individual files in kb_data/ directory (recommended for precise chunking)")
    print("2. victor_apps_consolidated.txt (single file with separators)")
    print("\nUpdate your knowledge base configuration to use these files.")

# Made with Bob
