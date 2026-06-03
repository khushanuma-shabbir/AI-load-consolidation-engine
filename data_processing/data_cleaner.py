"""
Data Cleaning Module
Automatically cleans all datasets and handles data quality issues
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class DataCleaner:
    """Comprehensive data cleaning for logistics datasets"""
    
    def __init__(self, datasets: Dict[str, pd.DataFrame]):
        self.datasets = datasets
        self.cleaned_datasets = {}
        self.cleaning_log = {}
        
    def clean_dataset(self, name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Clean a single dataset"""
        log = {
            'original_shape': df.shape,
            'operations': []
        }
        
        df_clean = df.copy()
        
        # 1. Remove duplicate rows
        duplicates_before = df_clean.duplicated().sum()
        if duplicates_before > 0:
            df_clean = df_clean.drop_duplicates()
            log['operations'].append(f"Removed {duplicates_before} duplicate rows")
        
        # 2. Handle date columns
        date_columns = [col for col in df_clean.columns if 'date' in col.lower() or 'time' in col.lower()]
        for col in date_columns:
            try:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                log['operations'].append(f"Parsed {col} as datetime")
            except:
                log['operations'].append(f"Failed to parse {col} as datetime")
        
        # 3. Handle missing values
        for col in df_clean.columns:
            missing_count = df_clean[col].isnull().sum()
            if missing_count > 0:
                if pd.api.types.is_numeric_dtype(df_clean[col]):
                    # For numeric: fill with median
                    median_val = df_clean[col].median()
                    df_clean[col].fillna(median_val, inplace=True)
                    log['operations'].append(f"Filled {missing_count} missing values in {col} with median ({median_val:.2f})")
                elif pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                    # For dates: forward fill
                    df_clean[col] = df_clean[col].ffill()
                    log['operations'].append(f"Forward-filled {missing_count} missing dates in {col}")
                else:
                    # For categorical: fill with 'Unknown' or mode
                    if df_clean[col].mode().empty:
                        df_clean[col].fillna('Unknown', inplace=True)
                        log['operations'].append(f"Filled {missing_count} missing values in {col} with 'Unknown'")
                    else:
                        mode_val = df_clean[col].mode()[0]
                        df_clean[col].fillna(mode_val, inplace=True)
                        log['operations'].append(f"Filled {missing_count} missing values in {col} with mode ('{mode_val}')")
        
        # 4. Fix data types
        # Convert ID columns to string
        id_columns = [col for col in df_clean.columns if col.endswith('_id')]
        for col in id_columns:
            df_clean[col] = df_clean[col].astype(str)
            log['operations'].append(f"Converted {col} to string")
        
        # 5. Handle outliers in numeric columns
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in id_columns:
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 3 * IQR
                upper_bound = Q3 + 3 * IQR
                
                outliers = ((df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)).sum()
                if outliers > 0 and outliers < len(df_clean) * 0.1:  # Only if < 10% outliers
                    df_clean[col] = df_clean[col].clip(lower=lower_bound, upper=upper_bound)
                    log['operations'].append(f"Clipped {outliers} outliers in {col}")
        
        # 6. Remove completely empty columns
        empty_cols = df_clean.columns[df_clean.isnull().all()].tolist()
        if empty_cols:
            df_clean = df_clean.drop(columns=empty_cols)
            log['operations'].append(f"Removed empty columns: {', '.join(empty_cols)}")
        
        # 7. Standardize text columns
        text_cols = df_clean.select_dtypes(include=['object']).columns
        for col in text_cols:
            if col not in id_columns:
                df_clean[col] = df_clean[col].str.strip()
                log['operations'].append(f"Stripped whitespace from {col}")
        
        log['final_shape'] = df_clean.shape
        log['rows_removed'] = log['original_shape'][0] - log['final_shape'][0]
        log['columns_removed'] = log['original_shape'][1] - log['final_shape'][1]
        
        self.cleaning_log[name] = log
        return df_clean
    
    def clean_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Clean all datasets"""
        print("CLEANING DATASETS...")
        print("="*80)
        
        for name, df in self.datasets.items():
            print(f"\nCleaning {name}...")
            cleaned_df = self.clean_dataset(name, df)
            self.cleaned_datasets[name] = cleaned_df
            print(f"✓ {name}: {df.shape} → {cleaned_df.shape}")
            print(f"  Operations: {len(self.cleaning_log[name]['operations'])}")
        
        return self.cleaned_datasets
    
    def save_cleaned_data(self, output_dir: str = "processed_data"):
        """Save cleaned datasets"""
        os.makedirs(output_dir, exist_ok=True)
        
        for name, df in self.cleaned_datasets.items():
            output_path = f"{output_dir}/{name}_cleaned.csv"
            df.to_csv(output_path, index=False)
            print(f"✓ Saved {output_path}")
        
        # Save cleaning log
        import json
        with open(f"{output_dir}/cleaning_log.json", 'w') as f:
            json.dump(self.cleaning_log, f, indent=2, default=str)
        
        print(f"\n✓ All cleaned datasets saved to {output_dir}/")
    
    def print_cleaning_summary(self):
        """Print cleaning summary"""
        print("\n" + "="*80)
        print("DATA CLEANING SUMMARY")
        print("="*80)
        
        for name, log in self.cleaning_log.items():
            print(f"\n{name.upper()}")
            print("-" * 80)
            print(f"Original: {log['original_shape'][0]:,} rows × {log['original_shape'][1]} columns")
            print(f"Cleaned:  {log['final_shape'][0]:,} rows × {log['final_shape'][1]} columns")
            print(f"Removed:  {log['rows_removed']} rows, {log['columns_removed']} columns")
            print(f"\nOperations performed: {len(log['operations'])}")
            for op in log['operations'][:10]:  # Show first 10 operations
                print(f"  - {op}")
            if len(log['operations']) > 10:
                print(f"  ... and {len(log['operations']) - 10} more operations")


class DataIntegrator:
    """Integrate and merge cleaned datasets"""
    
    def __init__(self, cleaned_datasets: Dict[str, pd.DataFrame]):
        self.datasets = cleaned_datasets
        self.unified_dataset = None
        
    def create_unified_dataset(self) -> pd.DataFrame:
        """Create unified logistics dataset by merging all relevant tables"""
        print("\n" + "="*80)
        print("CREATING UNIFIED LOGISTICS DATASET")
        print("="*80)
        
        # Start with trips as the main fact table
        if 'trips' not in self.datasets:
            print("Error: trips table not found")
            return None
        
        unified = self.datasets['trips'].copy()
        print(f"Starting with trips: {unified.shape}")
        
        # Merge loads (shipment details)
        if 'loads' in self.datasets:
            loads = self.datasets['loads'].copy()
            unified = unified.merge(
                loads,
                on='load_id',
                how='left',
                suffixes=('', '_load')
            )
            print(f"After merging loads: {unified.shape}")
        
        # Merge routes (distance and rate info)
        if 'routes' in self.datasets and 'route_id' in unified.columns:
            routes = self.datasets['routes'].copy()
            unified = unified.merge(
                routes,
                on='route_id',
                how='left',
                suffixes=('', '_route')
            )
            print(f"After merging routes: {unified.shape}")
        
        # Merge customers
        if 'customers' in self.datasets and 'customer_id' in unified.columns:
            customers = self.datasets['customers'].copy()
            unified = unified.merge(
                customers,
                on='customer_id',
                how='left',
                suffixes=('', '_customer')
            )
            print(f"After merging customers: {unified.shape}")
        
        # Merge drivers
        if 'drivers' in self.datasets and 'driver_id' in unified.columns:
            drivers = self.datasets['drivers'].copy()
            unified = unified.merge(
                drivers,
                on='driver_id',
                how='left',
                suffixes=('', '_driver')
            )
            print(f"After merging drivers: {unified.shape}")
        
        # Merge trucks
        if 'trucks' in self.datasets and 'truck_id' in unified.columns:
            trucks = self.datasets['trucks'].copy()
            unified = unified.merge(
                trucks,
                on='truck_id',
                how='left',
                suffixes=('', '_truck')
            )
            print(f"After merging trucks: {unified.shape}")
        
        # Merge trailers
        if 'trailers' in self.datasets and 'trailer_id' in unified.columns:
            trailers = self.datasets['trailers'].copy()
            unified = unified.merge(
                trailers,
                on='trailer_id',
                how='left',
                suffixes=('', '_trailer')
            )
            print(f"After merging trailers: {unified.shape}")
        
        self.unified_dataset = unified
        print(f"\n✓ Unified dataset created: {unified.shape[0]:,} rows × {unified.shape[1]} columns")
        
        return unified
    
    def generate_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate derived features for ML and optimization"""
        print("\n" + "="*80)
        print("GENERATING DERIVED FEATURES")
        print("="*80)
        
        df_enhanced = df.copy()
        
        # 1. shipment_weight_kg (if not already present)
        if 'weight' in df_enhanced.columns and 'shipment_weight_kg' not in df_enhanced.columns:
            df_enhanced['shipment_weight_kg'] = df_enhanced['weight']
            print("✓ Added shipment_weight_kg")
        
        # 2. utilization_percentage
        if 'shipment_weight_kg' in df_enhanced.columns and 'capacity_lbs' in df_enhanced.columns:
            df_enhanced['truck_capacity_kg'] = df_enhanced['capacity_lbs'] * 0.453592
            df_enhanced['utilization_percentage'] = (df_enhanced['shipment_weight_kg'] / df_enhanced['truck_capacity_kg']) * 100
            df_enhanced['utilization_percentage'] = df_enhanced['utilization_percentage'].clip(0, 100)
            print("✓ Added utilization_percentage")
        
        # 3. route_distance
        if 'distance_miles' in df_enhanced.columns and 'route_distance' not in df_enhanced.columns:
            df_enhanced['route_distance'] = df_enhanced['distance_miles']
            print("✓ Added route_distance")
        
        # 4. estimated_fuel_cost
        if 'fuel_gallons' in df_enhanced.columns and 'fuel_price_per_gallon' in df_enhanced.columns:
            df_enhanced['estimated_fuel_cost'] = df_enhanced['fuel_gallons'] * df_enhanced['fuel_price_per_gallon']
            print("✓ Added estimated_fuel_cost")
        elif 'distance_miles' in df_enhanced.columns:
            # Estimate: 6 MPG average, $3.50 per gallon
            df_enhanced['estimated_fuel_cost'] = (df_enhanced['distance_miles'] / 6.0) * 3.50
            print("✓ Added estimated_fuel_cost (estimated)")
        
        # 5. cost_per_trip
        if 'total_cost' in df_enhanced.columns and 'cost_per_trip' not in df_enhanced.columns:
            df_enhanced['cost_per_trip'] = df_enhanced['total_cost']
            print("✓ Added cost_per_trip")
        elif 'estimated_fuel_cost' in df_enhanced.columns:
            # Estimate total cost as 2x fuel cost (rough approximation)
            df_enhanced['cost_per_trip'] = df_enhanced['estimated_fuel_cost'] * 2.0
            print("✓ Added cost_per_trip (estimated)")
        
        # 6. emissions (CO2 in kg)
        if 'fuel_gallons' in df_enhanced.columns:
            # 1 gallon diesel = ~10.2 kg CO2
            df_enhanced['emissions'] = df_enhanced['fuel_gallons'] * 10.2
            print("✓ Added emissions (kg CO2)")
        elif 'distance_miles' in df_enhanced.columns:
            # Estimate: 6 MPG, 10.2 kg CO2 per gallon
            df_enhanced['emissions'] = (df_enhanced['distance_miles'] / 6.0) * 10.2
            print("✓ Added emissions (estimated)")
        
        # 7. truck_capacity_remaining
        if 'truck_capacity_kg' in df_enhanced.columns and 'shipment_weight_kg' in df_enhanced.columns:
            df_enhanced['truck_capacity_remaining'] = df_enhanced['truck_capacity_kg'] - df_enhanced['shipment_weight_kg']
            df_enhanced['truck_capacity_remaining'] = df_enhanced['truck_capacity_remaining'].clip(lower=0)
            print("✓ Added truck_capacity_remaining")
        
        # 8. revenue_per_mile
        if 'revenue' in df_enhanced.columns and 'distance_miles' in df_enhanced.columns:
            df_enhanced['revenue_per_mile'] = df_enhanced['revenue'] / df_enhanced['distance_miles'].replace(0, np.nan)
            print("✓ Added revenue_per_mile")
        
        # 9. profit_margin
        if 'revenue' in df_enhanced.columns and 'cost_per_trip' in df_enhanced.columns:
            df_enhanced['profit'] = df_enhanced['revenue'] - df_enhanced['cost_per_trip']
            df_enhanced['profit_margin'] = (df_enhanced['profit'] / df_enhanced['revenue'].replace(0, np.nan)) * 100
            print("✓ Added profit and profit_margin")
        
        # 10. cluster_id (placeholder, will be filled by clustering module)
        if 'cluster_id' not in df_enhanced.columns:
            df_enhanced['cluster_id'] = -1
            print("✓ Added cluster_id placeholder")
        
        print(f"\n✓ Enhanced dataset: {df_enhanced.shape[0]:,} rows × {df_enhanced.shape[1]} columns")
        
        return df_enhanced


if __name__ == "__main__":
    # This will be called from main pipeline
    pass
