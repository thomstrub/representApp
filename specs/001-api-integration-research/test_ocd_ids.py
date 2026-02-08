#!/usr/bin/env python3
"""
OCD-ID Testing Script - Phase 4 Research

Tests Google Civic Information API divisions endpoint with diverse addresses
to document OCD-ID structure, parsing rules, and integration patterns.

Tasks: T015-T020
"""

import json
import os
import sys
from typing import Dict, List, Any
import requests
from functools import lru_cache

# Test addresses for OCD-ID analysis
TEST_ADDRESSES = [
    # T015: Urban Seattle
    {
        "name": "Urban Seattle",
        "address": "1301 4th Ave, Seattle, WA 98101",
        "task": "T015",
        "category": "urban"
    },
    # T016: Rural Spokane
    {
        "name": "Rural Spokane",
        "address": "123 Main St, Spokane, WA 99201",
        "task": "T016",
        "category": "rural"
    },
    # T017: Zip code only
    {
        "name": "Zip Code Only",
        "address": "98101",
        "task": "T017",
        "category": "zip_only"
    },
    # T018: Military APO address
    {
        "name": "Military APO",
        "address": "PSC 1234, Box 5678, APO AP 96350",
        "task": "T018",
        "category": "military"
    },
    # T019: PO Box
    {
        "name": "PO Box Olympia",
        "address": "PO Box 123, Olympia, WA 98504",
        "task": "T019",
        "category": "po_box"
    },
    # T020: California address
    {
        "name": "California - San Francisco",
        "address": "1 Dr Carlton B Goodlett Pl, San Francisco, CA 94102",
        "task": "T020",
        "category": "multi_state"
    },
    # T020: New York address
    {
        "name": "New York - Manhattan",
        "address": "City Hall, New York, NY 10007",
        "task": "T020",
        "category": "multi_state"
    },
    # T020: Texas address
    {
        "name": "Texas - Austin",
        "address": "301 W 2nd St, Austin, TX 78701",
        "task": "T020",
        "category": "multi_state"
    },
    # T020: Florida address
    {
        "name": "Florida - Miami",
        "address": "3500 Pan American Dr, Miami, FL 33133",
        "task": "T020",
        "category": "multi_state"
    },
    # Additional Washington addresses for pattern validation
    {
        "name": "Washington - Bellevue",
        "address": "450 110th Ave NE, Bellevue, WA 98004",
        "task": "T020",
        "category": "additional"
    },
    {
        "name": "Washington - Tacoma",
        "address": "747 Market St, Tacoma, WA 98402",
        "task": "T020",
        "category": "additional"
    }
]

@lru_cache(maxsize=1)
def get_google_api_key() -> str:
    """
    Get Google Civic API key from environment variable
    
    Set via: export GOOGLE_CIVIC_API_KEY=your_key_here
    Or retrieve from AWS Parameter Store manually:
    aws ssm get-parameter --name /represent-app/api-keys/google-civic --with-decryption
    """
    api_key = os.environ.get('GOOGLE_CIVIC_API_KEY')
    if not api_key:
        raise ValueError(
            "GOOGLE_CIVIC_API_KEY environment variable not set.\n"
            "Retrieve from Parameter Store:\n"
            "  aws ssm get-parameter --name /represent-app/api-keys/google-civic --with-decryption --query 'Parameter.Value' --output text"
        )
    return api_key

def test_google_divisions(address: str) -> Dict[str, Any]:
    """
    Test Google Civic Information API representatives endpoint
    to get address-specific divisions and OCD-IDs
    
    Args:
        address: Full address or zip code to test
        
    Returns:
        API response with divisions, offices, and officials
    """
    api_key = get_google_api_key()
    url = "https://www.googleapis.com/civicinfo/v2/representatives"
    
    params = {
        "address": address,
        "key": api_key,
        "includeOffices": "true"
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    return response.json()

def analyze_ocd_id(ocd_id: str) -> Dict[str, str]:
    """
    Parse OCD-ID structure and extract components
    
    OCD-ID Format: ocd-division/country:us/state:wa/cd:7
    Components:
    - country: us
    - state: wa (2-letter state code)
    - division_type: cd (congressional district), sldu/sldl (state legislature), 
                     county, place, etc.
    - district: number or name
    
    Args:
        ocd_id: OCD division identifier
        
    Returns:
        Parsed components dictionary
    """
    parts = ocd_id.split('/')
    
    if len(parts) < 2 or parts[0] != 'ocd-division':
        return {"error": "Invalid OCD-ID format"}
    
    components = {}
    
    for part in parts[1:]:
        if ':' in part:
            key, value = part.split(':', 1)
            components[key] = value
    
    # Determine government level
    if 'place' in components or 'county' in components:
        components['level'] = 'local' if 'place' in components else 'county'
    elif 'sldl' in components or 'sldu' in components:
        components['level'] = 'state_legislature'
    elif 'cd' in components:
        components['level'] = 'federal_congress'
    elif 'state' in components and len(components) == 2:  # country + state only
        components['level'] = 'state'
    elif len(components) == 1:  # country only
        components['level'] = 'federal'
    else:
        components['level'] = 'other'
    
    return components

def test_all_addresses(save_to_file: bool = True) -> List[Dict[str, Any]]:
    """
    Test all addresses and collect OCD-ID patterns
    
    Args:
        save_to_file: Whether to save results to JSON file
        
    Returns:
        List of test results with OCD-ID analysis
    """
    results = []
    
    print("=" * 80)
    print("OCD-ID Testing Script - Phase 4 Research")
    print("=" * 80)
    print()
    
    for test in TEST_ADDRESSES:
        print(f"\n[{test['task']}] Testing: {test['name']}")
        print(f"  Address: {test['address']}")
        print(f"  Category: {test['category']}")
        
        try:
            response = test_google_divisions(test['address'])
            
            # Extract divisions from response
            # Note: Representatives endpoint returns divisions as a dictionary, not array
            divisions_dict = response.get('divisions', {})
            offices = response.get('offices', [])
            officials = response.get('officials', [])
            
            # Parse each OCD-ID
            ocd_analysis = []
            for ocd_id, division_data in divisions_dict.items():
                name = division_data.get('name', '')
                
                parsed = analyze_ocd_id(ocd_id)
                
                # Check if division has associated offices
                has_offices = any(
                    ocd_id in division_data.get('officeIndices', [])
                    for office in offices
                )
                
                ocd_analysis.append({
                    'ocd_id': ocd_id,
                    'name': name,
                    'components': parsed,
                    'has_offices': has_offices
                })
            
            result = {
                'test_name': test['name'],
                'task': test['task'],
                'category': test['category'],
                'address': test['address'],
                'success': True,
                'division_count': len(divisions_dict),
                'office_count': len(offices),
                'official_count': len(officials),
                'divisions': ocd_analysis
            }
            
            print(f"  ✅ Success: Found {len(divisions_dict)} divisions, {len(offices)} offices, {len(officials)} officials")
            
            # Display OCD-IDs
            for item in ocd_analysis:
                level = item['components'].get('level', 'unknown')
                has_reps = "✓" if item.get('has_offices', False) else " "
                print(f"     [{has_reps}] [{level}] {item['ocd_id']}")
                print(f"         Name: {item['name']}")
            
        except requests.exceptions.RequestException as e:
            result = {
                'test_name': test['name'],
                'task': test['task'],
                'category': test['category'],
                'address': test['address'],
                'success': False,
                'error': str(e),
                'divisions': []
            }
            print(f"  ❌ Error: {e}")
        
        results.append(result)
    
    if save_to_file:
        output_file = 'ocd-id-test-results.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n\n✅ Results saved to: {output_file}")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    successful_tests = sum(1 for r in results if r['success'])
    total_divisions = sum(r['division_count'] for r in results if r['success'])
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {len(results) - successful_tests}")
    print(f"Total divisions found: {total_divisions}")
    
    # Count by government level
    level_counts = {}
    for result in results:
        if result['success']:
            for div in result['divisions']:
                level = div['components'].get('level', 'unknown')
                level_counts[level] = level_counts.get(level, 0) + 1
    
    print("\nDivisions by government level:")
    for level, count in sorted(level_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {level}: {count}")
    
    return results

if __name__ == "__main__":
    try:
        results = test_all_addresses(save_to_file=True)
        
        # Exit with success if at least 80% of tests passed
        success_rate = sum(1 for r in results if r['success']) / len(results)
        sys.exit(0 if success_rate >= 0.8 else 1)
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
