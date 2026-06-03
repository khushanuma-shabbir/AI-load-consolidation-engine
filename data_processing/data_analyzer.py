"""
Data Analyzer Module
Automatically inspects, profiles, and analyzes all CSV datasets
"""

import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class DatasetAnalyzer:
    """Comprehensive dataset analyzer for logistics data"""
    
    def __init__(self, data_dir: str = "Dataset"):
        self.data_dir = data_dir
        self.datasets = {}
        self.data_dictionary = {}
        self.relationships = {}
        self.quality_report = {}
        
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load all CSV files from the dataset directory"""
        csv_files = list(Path(self.data_dir).glob("*.csv"))
        print(f"Found {len(csv_files)} CSV files\n")
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                dataset_name = csv_file.stem
                self.datasets[dataset_name] = df
                print(f"✓ Loaded {dataset_name}: {df.shape[0]} rows × {df.shape[1]} columns")
            except Exception as e:
                print(f"✗ Error loading {csv_file.name}: {str(e)}")
        
        return self.datasets
    
    def analyze_dataset(self, name: str, df: pd.DataFrame) -> Dict:
        """Comprehensive analysis of a single dataset"""
        analysis = {
            'name': name,
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'column_details': {},
            'missing_data': {},
            'duplicates': df.duplicated().sum(),
            'numeric_summary': {},
            'categorical_summary': {},
            'potential_keys': [],
            'date_columns': []
        }
        
        # Analyze each column
        for col in df.columns:
            col_info = {
                'dtype': str(df[col].dtype),
                'missing_count': df[col].isnull().sum(),
                'missing_pct': (df[col].isnull().sum() / len(df)) * 100,
                'unique_count': df[col].nunique(),
                'unique_pct': (df[col].nunique() / len(df)) * 100
            }
            
            # Identify potential primary keys
            if col_info['unique_count'] == len(df) and col_info['missing_count'] == 0:
                analysis['potential_keys'].append(col)
            
            # Detect date columns
            if 'date' in col.lower() or 'time' in col.lower():
                analysis['date_columns'].append(col)
            
            # Numeric column analysis
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info['min'] = df[col].min()
                col_info['max'] = df[col].max()
                col_info['mean'] = df[col].mean()
                col_info['median'] = df[col].median()
                col_info['std'] = df[col].std()
                col_info['zeros'] = (df[col] == 0).sum()
                col_info['negatives'] = (df[col] < 0).sum()
            
            # Categorical column analysis
            elif pd.api.types.is_object_dtype(df[col]):
                if col_info['unique_count'] < 50:
                    col_info['top_values'] = df[col].value_counts().head(10).to_dict()
            
            analysis['column_details'][col] = col_info
            
            if col_info['missing_count'] > 0:
                analysis['missing_data'][col] = {
                    'count': col_info['missing_count'],
                    'percentage': col_info['missing_pct']
                }
        
        return analysis
    
    def detect_relationships(self) -> Dict:
        """Detect foreign key relationships between datasets"""
        relationships = {}
        
        # Define known relationships from schema
        known_fks = {
            'loads': ['customer_id', 'route_id'],
            'trips': ['load_id', 'driver_id', 'truck_id', 'trailer_id'],
            'fuel_purchases': ['trip_id', 'truck_id', 'driver_id'],
            'maintenance_records': ['truck_id'],
            'delivery_events': ['load_id', 'trip_id', 'facility_id'],
            'safety_incidents': ['trip_id', 'truck_id', 'driver_id'],
            'driver_monthly_metrics': ['driver_id'],
            'truck_utilization_metrics': ['truck_id']
        }
        
        for dataset_name, fk_columns in known_fks.items():
            if dataset_name in self.datasets:
                relationships[dataset_name] = {}
                for fk in fk_columns:
                    if fk in self.datasets[dataset_name].columns:
                        # Find referenced table
                        ref_table = fk.replace('_id', '') + 's'
                        if ref_table.endswith('ss'):
                            ref_table = ref_table[:-1]
                        
                        relationships[dataset_name][fk] = {
                            'references': ref_table,
                            'foreign_key': fk
                        }
        
        self.relationships = relationships
        return relationships
    
    def generate_data_dictionary(self) -> Dict:
        """Generate comprehensive data dictionary"""
        for name, df in self.datasets.items():
            self.data_dictionary[name] = self.analyze_dataset(name, df)
        
        return self.data_dictionary
    
    def generate_quality_report(self) -> Dict:
        """Generate data quality assessment report"""
        quality_report = {
            'overall_summary': {},
            'dataset_quality': {},
            'issues_found': []
        }
        
        total_rows = sum(len(df) for df in self.datasets.values())
        total_cells = sum(df.size for df in self.datasets.values())
        total_missing = sum(df.isnull().sum().sum() for df in self.datasets.values())
        
        quality_report['overall_summary'] = {
            'total_datasets': len(self.datasets),
            'total_rows': total_rows,
            'total_cells': total_cells,
            'total_missing_cells': total_missing,
            'missing_percentage': (total_missing / total_cells) * 100 if total_cells > 0 else 0
        }
        
        # Per-dataset quality assessment
        for name, df in self.datasets.items():
            dataset_quality = {
                'completeness_score': 0,
                'duplicate_rows': df.duplicated().sum(),
                'missing_cells': df.isnull().sum().sum(),
                'issues': []
            }
            
            # Calculate completeness
            completeness = ((df.size - df.isnull().sum().sum()) / df.size) * 100
            dataset_quality['completeness_score'] = completeness
            
            # Identify issues
            if dataset_quality['duplicate_rows'] > 0:
                dataset_quality['issues'].append(f"Found {dataset_quality['duplicate_rows']} duplicate rows")
                quality_report['issues_found'].append(f"{name}: {dataset_quality['duplicate_rows']} duplicates")
            
            if dataset_quality['missing_cells'] > 0:
                dataset_quality['issues'].append(f"Found {dataset_quality['missing_cells']} missing values")
            
            if completeness < 95:
                quality_report['issues_found'].append(f"{name}: Low completeness ({completeness:.1f}%)")
            
            quality_report['dataset_quality'][name] = dataset_quality
        
        self.quality_report = quality_report
        return quality_report
    
    def save_reports(self, output_dir: str = "reports"):
        """Save all analysis reports"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save data dictionary
        with open(f"{output_dir}/data_dictionary.json", 'w') as f:
            json.dump(self.data_dictionary, f, indent=2, default=str)
        
        # Save relationships
        with open(f"{output_dir}/relationships.json", 'w') as f:
            json.dump(self.relationships, f, indent=2)
        
        # Save quality report
        with open(f"{output_dir}/quality_report.json", 'w') as f:
            json.dump(self.quality_report, f, indent=2, default=str)
        
        print(f"\n✓ Reports saved to {output_dir}/")
    
    def print_summary(self):
        """Print analysis summary to console"""
        print("\n" + "="*80)
        print("DATASET ANALYSIS SUMMARY")
        print("="*80)
        
        for name, analysis in self.data_dictionary.items():
            print(f"\n{name.upper()}")
            print("-" * 80)
            print(f"Rows: {analysis['rows']:,} | Columns: {analysis['columns']}")
            print(f"Memory: {analysis['memory_usage_mb']:.2f} MB")
            print(f"Duplicates: {analysis['duplicates']}")
            
            if analysis['potential_keys']:
                print(f"Primary Key Candidates: {', '.join(analysis['potential_keys'])}")
            
            if analysis['date_columns']:
                print(f"Date Columns: {', '.join(analysis['date_columns'])}")
            
            if analysis['missing_data']:
                print(f"Missing Data in {len(analysis['missing_data'])} columns:")
                for col, info in list(analysis['missing_data'].items())[:5]:
                    print(f"  - {col}: {info['count']} ({info['percentage']:.1f}%)")
        
        print("\n" + "="*80)
        print("RELATIONSHIPS DETECTED")
        print("="*80)
        for dataset, fks in self.relationships.items():
            if fks:
                print(f"\n{dataset}:")
                for fk, info in fks.items():
                    print(f"  - {fk} → {info['references']}")
        
        print("\n" + "="*80)
        print("DATA QUALITY SUMMARY")
        print("="*80)
        qr = self.quality_report['overall_summary']
        print(f"Total Datasets: {qr['total_datasets']}")
        print(f"Total Rows: {qr['total_rows']:,}")
        print(f"Overall Completeness: {100 - qr['missing_percentage']:.2f}%")
        print(f"\nIssues Found: {len(self.quality_report['issues_found'])}")
        for issue in self.quality_report['issues_found'][:10]:
            print(f"  - {issue}")


if __name__ == "__main__":
    # Initialize analyzer
    analyzer = DatasetAnalyzer("Dataset")
    
    # Load all datasets
    print("LOADING DATASETS...")
    print("="*80)
    analyzer.load_all_datasets()
    
    # Generate data dictionary
    print("\n\nGENERATING DATA DICTIONARY...")
    print("="*80)
    analyzer.generate_data_dictionary()
    
    # Detect relationships
    print("\n\nDETECTING RELATIONSHIPS...")
    print("="*80)
    analyzer.detect_relationships()
    
    # Generate quality report
    print("\n\nGENERATING QUALITY REPORT...")
    print("="*80)
    analyzer.generate_quality_report()
    
    # Print summary
    analyzer.print_summary()
    
    # Save reports
    analyzer.save_reports()
    
    print("\n\n✓ Analysis complete!")
