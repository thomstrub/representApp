/**
 * Elected representative information
 * Matches backend API response from feature 003-address-lookup
 */
export interface Representative {
  /** Unique identifier (format: OpenStates ID) */
  id: string;
  
  /** Full name of the representative */
  name: string;
  
  /** Official title/office (e.g., "U.S. Senator", "State Representative") */
  office: string;
  
  /** Party affiliation (e.g., "Democratic", "Republican", "Independent") */
  party: string | null;
  
  /** Government level for categorization */
  government_level: 'federal' | 'state' | 'local';
  
  /** Human-readable district */
  jurisdiction: string;
  
  /** Email address (optional) */
  email?: string | null;
  
  /** Phone number (optional) */
  phone?: string | null;
  
  /** Physical office address (optional) */
  address?: string | null;
  
  /** Official website URL (optional) */
  website?: string | null;
  
  /** Photo URL (optional) */
  photo_url?: string | null;
}
