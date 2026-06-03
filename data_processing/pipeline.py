"""
Data Processing Pipeline
Orchestrates the complete data analysis, cleaning, and integration process
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from data_processing.data_analyzer import DatasetAnalyzer
from data_processing.data_cleaner import DataCleaner, DataIntegrator


def run_complete_pipeline():
    """Execute the complete data processing pipeline"""
    
    print("="*80)
    print("AI LOAD CONSOLIDATION - DATA PROCESSING PIPELINE")
    print("="*80)
    
    # STEP 1: Analyze datasets
    print("\n\nSTEP 1: DATASET ANALYSIS")
    print("="*80)
    analyzer = DatasetAnalyzer("Dataset")
    datasets = analyzer.load_all_datasets()
    analyzer.generate_data_dictionary()
    analyzer.detect_relationships()
    analyzer.generate_quality_report()
    analyzer.print_summary()
    analyzer.save_reports("reports")
    
    # STEP 2: Clean datasets
    print("\n\n\nSTEP 2: DATA CLEANING")
    print("="*80)
    cleaner = DataCleaner(datasets)
    cleaned_datasets = cleaner.clean_all_datasets()
    cleaner.print_cleaning_summary()
    cleaner.save_cleaned_data("processed_data")
    
    # STEP 3: Integrate datasets
    print("\n\n\nSTEP 3: DATA INTEGRATION")
    print("="*80)
    integrator = DataIntegrator(cleaned_datasets)
    unified_dataset = integrator.create_unified_dataset()
    
    if unified_dataset is not None:
        # STEP 4: Generate derived features
        enhanced_dataset = integrator.generate_derived_features(unified_dataset)
        
        # Save unified dataset
        enhanced_dataset.to_csv("processed_data/unified_logistics_dataset.csv", index=False)
        print(f"\n✓ Saved unified dataset: processed_data/unified_logistics_dataset.csv")
        
        # Save feature summary
        feature_summary = {
            'total_rows': len(enhanced_dataset),
            'total_features': len(enhanced_dataset.columns),
            'features': list(enhanced_dataset.columns),
            'numeric_features': list(enhanced_dataset.select_dtypes(include=['number']).columns),
            'categorical_features': list(enhanced_dataset.select_dtypes(include=['object']).columns),
            'datetime_features': list(enhanced_dataset.select_dtypes(include=['datetime64']).columns)
        }
        
        import json
        with open("processed_data/feature_summary.json", 'w') as f:
            json.dump(feature_summary, f, indent=2, default=str)
        
        print("\n" + "="*80)
        print("PIPELINE COMPLETE")
        print("="*80)
        print(f"✓ Analyzed {len(datasets)} datasets")
        print(f"✓ Cleaned and saved all datasets")
        print(f"✓ Created unified dataset with {len(enhanced_dataset):,} rows and {len(enhanced_dataset.columns)} features")
        print(f"✓ Generated reports in reports/")
        print(f"✓ Saved processed data in processed_data/")
        print("\n✓ Ready for AI module implementation!")
        
        return enhanced_dataset
    else:
        print("Error: Failed to create unified dataset")
        return None


if __name__ == "__main__":
    run_complete_pipeline()
