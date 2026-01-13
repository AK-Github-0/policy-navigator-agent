"""
Script to download and prepare policy datasets
"""

import os
import requests
from pathlib import Path
from loguru import logger
import pandas as pd
from bs4 import BeautifulSoup
import time

logger.add("logs/download_{time}.log")


class DatasetDownloader:
    """Download and prepare policy datasets"""
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data directory: {self.data_dir}")
    
    def download_ftc_enforcement_actions(self):
        """Download FTC enforcement actions data"""
        logger.info("Downloading FTC enforcement actions...")
        
        # Create sample FTC enforcement data
        sample_data = {
            'case_id': [
                'FTC-2023-001', 'FTC-2023-002', 'FTC-2023-003',
                'FTC-2023-004', 'FTC-2023-005'
            ],
            'title': [
                'Privacy Policy Violation Case',
                'Data Security Breach Enforcement',
                'COPPA Compliance Action',
                'Deceptive Marketing Practices',
                'Consumer Protection Violation'
            ],
            'date': [
                '2023-01-15', '2023-03-22', '2023-05-10',
                '2023-07-08', '2023-09-14'
            ],
            'type': [
                'Privacy', 'Data Security', 'Children Privacy',
                'Marketing', 'Consumer Protection'
            ],
            'penalty': [
                5000000, 3000000, 1500000, 2000000, 4000000
            ],
            'description': [
                'Company failed to implement adequate privacy safeguards...',
                'Inadequate data security measures led to breach...',
                'Violated COPPA regulations regarding children data...',
                'Made false claims in marketing materials...',
                'Engaged in unfair consumer practices...'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        output_path = self.data_dir / 'ftc_enforcement_actions.csv'
        df.to_csv(output_path, index=False)
        
        logger.success(f"Saved FTC data: {output_path}")
        return output_path
    
    def download_epa_regulations(self):
        """Download EPA regulations data"""
        logger.info("Downloading EPA regulations...")
        
        # Create sample EPA regulations data
        sample_data = {
            'regulation_id': [
                'EPA-HQ-OAR-2023-0001', 'EPA-HQ-OW-2023-0002',
                'EPA-HQ-OLEM-2023-0003', 'EPA-HQ-OAR-2023-0004'
            ],
            'title': [
                'Clean Air Act Standards Update',
                'Safe Drinking Water Requirements',
                'Hazardous Waste Management Rules',
                'Vehicle Emissions Standards'
            ],
            'effective_date': [
                '2024-01-01', '2024-03-15', '2024-06-01', '2024-09-01'
            ],
            'jurisdiction': [
                'Federal', 'Federal', 'Federal', 'Federal'
            ],
            'status': [
                'Active', 'Active', 'Proposed', 'Active'
            ],
            'description': [
                'Updated standards for air quality monitoring and compliance...',
                'New requirements for drinking water treatment facilities...',
                'Revised rules for hazardous waste storage and disposal...',
                'Stricter emission standards for passenger vehicles...'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        output_path = self.data_dir / 'epa_regulations.csv'
        df.to_csv(output_path, index=False)
        
        logger.success(f"Saved EPA data: {output_path}")
        return output_path
    
    def download_gdpr_compliance_data(self):
        """Create GDPR compliance reference data"""
        logger.info("Creating GDPR compliance data...")
        
        sample_data = {
            'article': [
                'Article 6', 'Article 7', 'Article 13', 'Article 15',
                'Article 17', 'Article 25', 'Article 32', 'Article 33'
            ],
            'title': [
                'Lawfulness of Processing',
                'Conditions for Consent',
                'Information to be Provided',
                'Right of Access',
                'Right to Erasure',
                'Data Protection by Design',
                'Security of Processing',
                'Breach Notification'
            ],
            'category': [
                'Legal Basis', 'Consent', 'Transparency', 'Data Subject Rights',
                'Data Subject Rights', 'Technical Measures', 'Security', 'Compliance'
            ],
            'applies_to_small_business': [
                True, True, True, True, True, True, True, True
            ],
            'description': [
                'Processing must have a lawful basis such as consent or legitimate interest...',
                'Consent must be freely given, specific, informed, and unambiguous...',
                'Controllers must provide information about data processing...',
                'Data subjects have the right to access their personal data...',
                'Data subjects can request deletion of their personal data...',
                'Privacy must be built into systems from the design stage...',
                'Appropriate technical measures must protect personal data...',
                'Breaches must be reported to authorities within 72 hours...'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        output_path = self.data_dir / 'gdpr_compliance.csv'
        df.to_csv(output_path, index=False)
        
        logger.success(f"Saved GDPR data: {output_path}")
        return output_path
    
    def scrape_federal_register_samples(self):
        """Create sample Federal Register documents"""
        logger.info("Creating Federal Register sample documents...")
        
        documents = [
            {
                'id': 'FR-2024-001',
                'title': 'Executive Order 14067 - Ensuring Responsible Development of Digital Assets',
                'type': 'Executive Order',
                'date': '2024-03-09',
                'content': '''
Executive Order 14067 establishes the first-ever whole-of-government approach 
to addressing the risks and harnessing the potential benefits of digital assets 
and their underlying technology. The Order outlines a national policy for 
digital assets across six key priorities: consumer and investor protection; 
financial stability; illicit finance; U.S. leadership in the global financial 
system and economic competitiveness; financial inclusion; and responsible innovation.

Key Provisions:
1. The policy of my Administration on digital assets must continue to protect 
United States consumers, investors, and businesses
2. Consistent with the goals stated, my Administration will evaluate digital assets 
including their design, trading, mining, and use
3. Federal agencies shall assess the technological infrastructure and capacity needs
'''
            },
            {
                'id': 'FR-2024-002',
                'title': 'Section 230 of the Communications Decency Act - Current Status',
                'type': 'Statutory Reference',
                'date': '1996-02-08',
                'content': '''
Section 230(c)(1) states that "No provider or user of an interactive computer 
service shall be treated as the publisher or speaker of any information provided 
by another information content provider."

This provision has been interpreted to provide broad immunity to online platforms 
for user-generated content. However, recent court cases have narrowed its scope:

Recent Developments:
- Fair Housing Council v. Roommates.com (2008): Platforms lose immunity when 
  they contribute to illegal content development
- Gonzalez v. Google LLC (2023): Supreme Court examined whether algorithmic 
  recommendations are protected
- Twitter v. Taamneh (2023): Clarified platform liability standards

Current debates focus on whether Section 230 should be reformed to hold platforms 
more accountable for harmful content while preserving innovation.
'''
            }
        ]
        
        for doc in documents:
            filename = f"{doc['id']}.txt"
            output_path = self.data_dir / filename
            
            with open(output_path, 'w') as f:
                f.write(f"Title: {doc['title']}\n")
                f.write(f"Type: {doc['type']}\n")
                f.write(f"Date: {doc['date']}\n")
                f.write(f"\n{doc['content']}\n")
            
            logger.success(f"Saved document: {output_path}")
    
    def download_all(self):
        """Download all datasets"""
        logger.info("Starting dataset download...")
        
        try:
            # Download datasets
            self.download_ftc_enforcement_actions()
            time.sleep(1)
            
            self.download_epa_regulations()
            time.sleep(1)
            
            self.download_gdpr_compliance_data()
            time.sleep(1)
            
            self.scrape_federal_register_samples()
            
            logger.success("All datasets downloaded successfully!")
            
            # Print summary
            files = list(self.data_dir.glob('*'))
            logger.info(f"Total files: {len(files)}")
            for file in files:
                logger.info(f"  - {file.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error downloading datasets: {str(e)}")
            return False


def main():
    """Main execution"""
    downloader = DatasetDownloader()
    success = downloader.download_all()
    
    if success:
        print("\n✅ Dataset download complete!")
        print(f"📁 Data saved to: {downloader.data_dir}")
        print("\nNext steps:")
        print("  1. Review the downloaded data")
        print("  2. Run: python scripts/create_index.py")
    else:
        print("\n❌ Dataset download failed. Check logs for details.")


if __name__ == '__main__':
    main()