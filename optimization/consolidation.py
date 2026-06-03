"""
AI MODULE 2: Load Consolidation Engine
Implements First Fit Decreasing Bin Packing to maximize truck utilization
"""

import pandas as pd
import numpy as np
import json
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')


class BinPackingOptimizer:
    """First Fit Decreasing bin packing for load consolidation"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.bins = []  # List of trucks with assigned loads
        self.unassigned_loads = []
        self.optimization_metrics = {}
        
    def prepare_loads(self) -> List[Dict]:
        """
        Prepare and sort loads by weight (descending)
        """
        loads = []
        
        # Determine weight column
        weight_col = None
        for col in ['weight', 'shipment_weight_kg', 'load_weight']:
            if col in self.data.columns:
                weight_col = col
                break
        
        if weight_col is None:
            print("Warning: No weight column found, using default 1000 lbs")
            self.data['weight'] = 1000
            weight_col = 'weight'
        
        # Create load objects
        for idx, row in self.data.iterrows():
            load = {
                'load_id': row.get('load_id', f'LOAD_{idx}'),
                'weight': float(row[weight_col]),
                'revenue': float(row.get('revenue', 0)),
                'distance': float(row.get('distance_miles', 0)),
                'destination': row.get('destination_city', 'Unknown'),
                'cluster_id': row.get('cluster_id', -1)
            }
            loads.append(load)
        
        # Sort by weight (descending) for First Fit Decreasing
        loads.sort(key=lambda x: x['weight'], reverse=True)
        
        return loads
    
    def get_truck_capacity(self) -> float:
        """
        Determine truck capacity from data
        """
        # Check for capacity in data
        if 'capacity_lbs' in self.data.columns:
            capacity = self.data['capacity_lbs'].median()
        elif 'truck_capacity_kg' in self.data.columns:
            capacity = self.data['truck_capacity_kg'].median()
        else:
            # Default capacity: 45,000 lbs (standard semi-trailer)
            capacity = 45000
        
        return float(capacity)
    
    def first_fit_decreasing(self, loads: List[Dict], truck_capacity: float) -> List[Dict]:
        """
        First Fit Decreasing bin packing algorithm
        """
        bins = []
        
        for load in loads:
            placed = False
            
            # Try to fit in existing bins
            for bin_idx, truck_bin in enumerate(bins):
                if truck_bin['remaining_capacity'] >= load['weight']:
                    # Add load to this bin
                    truck_bin['loads'].append(load)
                    truck_bin['remaining_capacity'] -= load['weight']
                    truck_bin['utilization'] = ((truck_capacity - truck_bin['remaining_capacity']) / truck_capacity) * 100
                    truck_bin['total_revenue'] += load['revenue']
                    truck_bin['total_distance'] += load['distance']
                    placed = True
                    break
            
            # If not placed, create new bin
            if not placed:
                new_bin = {
                    'truck_id': f'TRUCK_{len(bins) + 1}',
                    'capacity': truck_capacity,
                    'remaining_capacity': truck_capacity - load['weight'],
                    'utilization': (load['weight'] / truck_capacity) * 100,
                    'loads': [load],
                    'total_revenue': load['revenue'],
                    'total_distance': load['distance']
                }
                bins.append(new_bin)
        
        return bins
    
    def optimize_consolidation(self):
        """
        Run load consolidation optimization
        """
        print("="*80)
        print("LOAD CONSOLIDATION OPTIMIZATION")
        print("="*80)
        
        # Prepare loads
        print("\nPreparing loads...")
        loads = self.prepare_loads()
        print(f"✓ Prepared {len(loads)} loads")
        print(f"  Total Weight: {sum(l['weight'] for l in loads):,.2f} lbs")
        print(f"  Total Revenue: ${sum(l['revenue'] for l in loads):,.2f}")
        
        # Get truck capacity
        truck_capacity = self.get_truck_capacity()
        print(f"  Truck Capacity: {truck_capacity:,.2f} lbs")
        
        # Calculate before optimization metrics
        unique_trucks_before = len(self.data['truck_id'].unique()) if 'truck_id' in self.data.columns else len(loads)
        print(f"\nBEFORE OPTIMIZATION:")
        print(f"  Trucks Used: {unique_trucks_before}")
        
        # Run First Fit Decreasing
        print("\nRunning First Fit Decreasing algorithm...")
        self.bins = self.first_fit_decreasing(loads, truck_capacity)
        
        # Calculate metrics
        trucks_used = len(self.bins)
        avg_utilization = np.mean([b['utilization'] for b in self.bins])
        total_remaining = sum(b['remaining_capacity'] for b in self.bins)
        trucks_saved = unique_trucks_before - trucks_used
        savings_percentage = (trucks_saved / unique_trucks_before) * 100 if unique_trucks_before > 0 else 0
        
        # Utilization distribution
        util_bins = [b['utilization'] for b in self.bins]
        high_util = sum(1 for u in util_bins if u >= 80)
        medium_util = sum(1 for u in util_bins if 60 <= u < 80)
        low_util = sum(1 for u in util_bins if u < 60)
        
        self.optimization_metrics = {
            'before': {
                'trucks_used': unique_trucks_before,
                'avg_utilization': 'Unknown'
            },
            'after': {
                'trucks_used': trucks_used,
                'avg_utilization': avg_utilization,
                'high_utilization_trucks': high_util,
                'medium_utilization_trucks': medium_util,
                'low_utilization_trucks': low_util
            },
            'improvement': {
                'trucks_saved': trucks_saved,
                'savings_percentage': savings_percentage,
                'capacity_wasted_before': 'Unknown',
                'capacity_wasted_after': total_remaining,
                'efficiency_gain': f"{savings_percentage:.1f}%"
            },
            'economics': {
                'cost_per_truck': 500,  # Estimated
                'cost_savings': trucks_saved * 500,
                'total_revenue': sum(b['total_revenue'] for b in self.bins)
            }
        }
        
        print(f"\nAFTER OPTIMIZATION:")
        print(f"  Trucks Used: {trucks_used}")
        print(f"  Average Utilization: {avg_utilization:.2f}%")
        print(f"  Trucks Saved: {trucks_saved} ({savings_percentage:.1f}%)")
        print(f"\nUTILIZATION BREAKDOWN:")
        print(f"  High (≥80%): {high_util} trucks")
        print(f"  Medium (60-80%): {medium_util} trucks")
        print(f"  Low (<60%): {low_util} trucks")
        print(f"\nCOST SAVINGS:")
        print(f"  Estimated: ${self.optimization_metrics['economics']['cost_savings']:,.2f}")
        
        return self.bins
    
    def generate_comparison_report(self) -> pd.DataFrame:
        """
        Generate before/after comparison
        """
        comparison = pd.DataFrame([
            {
                'Metric': 'Trucks Used',
                'Before': self.optimization_metrics['before']['trucks_used'],
                'After': self.optimization_metrics['after']['trucks_used'],
                'Change': f"-{self.optimization_metrics['improvement']['trucks_saved']}"
            },
            {
                'Metric': 'Average Utilization',
                'Before': self.optimization_metrics['before']['avg_utilization'],
                'After': f"{self.optimization_metrics['after']['avg_utilization']:.2f}%",
                'Change': 'Improved'
            },
            {
                'Metric': 'High Utilization Trucks',
                'Before': 'Unknown',
                'After': self.optimization_metrics['after']['high_utilization_trucks'],
                'Change': '+' + str(self.optimization_metrics['after']['high_utilization_trucks'])
            },
            {
                'Metric': 'Cost Savings',
                'Before': '$0',
                'After': f"${self.optimization_metrics['economics']['cost_savings']:,.2f}",
                'Change': f"+${self.optimization_metrics['economics']['cost_savings']:,.2f}"
            }
        ])
        
        return comparison
    
    def export_assignments(self) -> pd.DataFrame:
        """
        Export truck assignments as DataFrame
        """
        assignments = []
        
        for truck_bin in self.bins:
            for load in truck_bin['loads']:
                assignments.append({
                    'truck_id': truck_bin['truck_id'],
                    'load_id': load['load_id'],
                    'load_weight': load['weight'],
                    'truck_capacity': truck_bin['capacity'],
                    'truck_utilization': truck_bin['utilization'],
                    'remaining_capacity': truck_bin['remaining_capacity'],
                    'destination': load['destination'],
                    'revenue': load['revenue']
                })
        
        return pd.DataFrame(assignments)
    
    def save_results(self, output_dir: str = "optimization/results"):
        """
        Save consolidation results
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save optimization metrics
        with open(f"{output_dir}/consolidation_metrics.json", 'w') as f:
            json.dump(self.optimization_metrics, f, indent=2)
        
        # Save truck assignments
        assignments_df = self.export_assignments()
        assignments_df.to_csv(f"{output_dir}/truck_assignments.csv", index=False)
        
        # Save comparison report
        comparison_df = self.generate_comparison_report()
        comparison_df.to_csv(f"{output_dir}/consolidation_comparison.csv", index=False)
        
        # Save bin summary
        bin_summary = []
        for bin_info in self.bins:
            bin_summary.append({
                'truck_id': bin_info['truck_id'],
                'num_loads': len(bin_info['loads']),
                'utilization': bin_info['utilization'],
                'remaining_capacity': bin_info['remaining_capacity'],
                'total_revenue': bin_info['total_revenue'],
                'total_distance': bin_info['total_distance']
            })
        pd.DataFrame(bin_summary).to_csv(f"{output_dir}/truck_summary.csv", index=False)
        
        print(f"\n✓ Consolidation results saved to {output_dir}/")


def run_consolidation(data_path: str = "optimization/results/shipments_clustered.csv"):
    """
    Main function to run load consolidation
    """
    print("\n" + "="*80)
    print("AI MODULE 2: LOAD CONSOLIDATION ENGINE")
    print("="*80)
    
    # Load data
    print("\nLoading data...")
    data = pd.read_csv(data_path)
    print(f"✓ Loaded {len(data):,} shipments")
    
    # Initialize optimizer
    optimizer = BinPackingOptimizer(data)
    
    # Run optimization
    bins = optimizer.optimize_consolidation()
    
    # Save results
    optimizer.save_results()
    
    print("\n✓ Load consolidation complete!")
    
    return optimizer


if __name__ == "__main__":
    run_consolidation()
