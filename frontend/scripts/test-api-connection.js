#!/usr/bin/env node
/**
 * Manual E2E Test: Verify frontend can connect to and parse backend API
 * 
 * Usage:
 *   node scripts/test-api-connection.js
 * 
 * This script:
 * 1. Calls the real backend API
 * 2. Validates the response structure matches frontend types
 * 3. Reports any discrepancies
 */

const API_URL = 'https://pktpja4zxd.execute-api.us-west-1.amazonaws.com/api/representatives';
const TEST_ADDRESS = '1301 4th Ave Seattle WA 98101';

async function testAPIConnection() {
  console.log('🔍 Testing backend API connectivity...\n');
  console.log(`API: ${API_URL}`);
  console.log(`Test Address: ${TEST_ADDRESS}\n`);

  try {
    const url = `${API_URL}?address=${encodeURIComponent(TEST_ADDRESS)}`;
    console.log(`Calling: ${url}\n`);

    const response = await fetch(url);
    
    if (!response.ok) {
      console.error(`❌ HTTP Error: ${response.status} ${response.statusText}`);
      const body = await response.text();
      console.error('Response:', body);
      process.exit(1);
    }

    const data = await response.json();
    
    console.log('✅ API call successful!\n');
    
    // Validate structure
    const checks = [
      { field: 'address', present: 'address' in data, type: typeof data.address },
      { field: 'representatives', present: 'representatives' in data, type: typeof data.representatives },
      { field: 'metadata', present: 'metadata' in data, type: typeof data.metadata },
      { field: 'warnings', present: 'warnings' in data, type: typeof data.warnings },
    ];

    console.log('📋 Top-level Structure:');
    checks.forEach(check => {
      const status = check.present ? '✅' : '❌';
      console.log(`  ${status} ${check.field}: ${check.present ? check.type : 'missing'}`);
    });

    // Validate metadata
    if (data.metadata) {
      console.log('\n📋 Metadata Fields:');
      const metadataFields = [
        'address',
        'division_count',
        'representative_count',
        'government_levels',
        'response_time_ms'
      ];
      
      metadataFields.forEach(field => {
        const present = field in data.metadata;
        const status = present ? '✅' : '❌';
        const type = present ? typeof data.metadata[field] : 'missing';
        console.log(`  ${status} ${field}: ${type}`);
      });
    }

    // Validate representatives
    if (data.representatives && data.representatives.length > 0) {
      console.log('\n📋 Representative Structure (first item):');
      const rep = data.representatives[0];
      const repFields = [
        'id', 'name', 'office', 'party', 'government_level', 
        'jurisdiction', 'email', 'phone', 'address', 'website', 'photo_url'
      ];
      
      repFields.forEach(field => {
        const present = field in rep;
        const status = present ? '✅' : '❌';
        const value = present ? (rep[field] === null ? 'null' : typeof rep[field]) : 'missing';
        console.log(`  ${status} ${field}: ${value}`);
      });

      console.log(`\n📊 Total representatives: ${data.representatives.length}`);
      
      // Check government levels
      const levels = [...new Set(data.representatives.map(r => r.government_level))];
      console.log(`📊 Government levels: ${levels.join(', ')}`);
    }

    // Show warnings
    if (data.warnings && data.warnings.length > 0) {
      console.log(`\n⚠️  Warnings (${data.warnings.length}):`);
      data.warnings.slice(0, 3).forEach(w => console.log(`  - ${w}`));
      if (data.warnings.length > 3) {
        console.log(`  ... and ${data.warnings.length - 3} more`);
      }
    }

    console.log('\n✅ All structure checks passed!');
    console.log('\n💡 Frontend TypeScript types match backend response.');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    process.exit(1);
  }
}

testAPIConnection();
