"""
Smart Dispatch Planner - Core Module
Intelligent dispatch planning with AI-powered truck allocation and route optimization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import os


class SmartDispatcher:
    """
    Intelligent Dispatch System
    - Finds consolidation opportunities
    - Allocates optimal trucks
    - Calculates routes and costs
    - Generates dispatch plans
    """
    
    def __init__(self, data_path: str = "processed_data/unified_logistics_dataset.csv"):
        """Initialize dispatcher with cleaned logistics data"""
        self.data = pd.read_csv(data_path)
        self.trucks = self._load_truck_data()
        self.active_loads = self._get_active_loads()
        
    def _load_truck_data(self) -> pd.DataFrame:
        """Load truck fleet data"""
        if os.path.exists("processed_data/trucks_cleaned.csv"):
            trucks = pd.read_csv("processed_data/trucks_cleaned.csv")
        else:
            # Extract from unified dataset
            trucks = self.data[['truck_id', 'make', 'capacity_lbs', 'fuel_type', 'status']].drop_duplicates()
        
        # Ensure capacity column exists
        if 'capacity_lbs' not in trucks.columns and 'capacity' in trucks.columns:
            trucks['capacity_lbs'] = trucks['capacity']
        elif 'capacity_lbs' not in trucks.columns:
            trucks['capacity_lbs'] = 45000  # Default capacity
            
        return trucks
    
    def _get_active_loads(self) -> pd.DataFrame:
        """Get currently active loads from database"""
        # Simulate active loads - in production, query from database
        active = self.data.sample(min(100, len(self.data))).copy()
        active['status'] = 'in_transit'
        active['remaining_capacity'] = active.get('capacity_lbs', 45000) * 0.3  # 30% remaining on average
        return active
    
    def find_consolidation_opportunities(self, 
                                        source: str,
                                        destination: str,
                                        weight: float,
                                        priority: str) -> List[Dict]:
        """
        Find existing trucks that can consolidate this shipment
        """
        opportunities = []
        
        # Search for trucks heading to same/nearby destination
        if 'destination_city' in self.active_loads.columns:
            similar_dest = self.active_loads[
                self.active_loads['destination_city'].str.contains(destination, case=False, na=False)
            ]
        else:
            similar_dest = self.active_loads.head(10)  # Fallback
        
        for idx, load in similar_dest.iterrows():
            truck_capacity = load.get('capacity_lbs', 45000)
            remaining_capacity = load.get('remaining_capacity', truck_capacity * 0.3)
            
            # Check if weight fits
            if remaining_capacity >= weight:
                utilization_before = ((truck_capacity - remaining_capacity) / truck_capacity) * 100
                utilization_after = ((truck_capacity - remaining_capacity + weight) / truck_capacity) * 100
                
                opportunities.append({
                    'truck_id': load.get('truck_id', f'TRK-{idx}'),
                    'current_utilization': utilization_before,
                    'new_utilization': utilization_after,
                    'remaining_capacity': remaining_capacity - weight,
                    'capacity_lbs': truck_capacity,
                    'consolidation_possible': True,
                    'score': utilization_after  # Higher utilization = better
                })
        
        # Sort by score (best opportunities first)
        opportunities = sorted(opportunities, key=lambda x: x['score'], reverse=True)
        return opportunities
    
    def select_best_truck(self, opportunities: List[Dict], weight: float) -> Optional[Dict]:
        """
        Select the best truck from consolidation opportunities
        If none available, allocate new truck
        """
        if opportunities:
            # Return best consolidation opportunity
            return opportunities[0]
        else:
            # Allocate new truck
            available_trucks = self.trucks[self.trucks['status'] != 'maintenance'].head(1)
            
            if len(available_trucks) > 0:
                truck = available_trucks.iloc[0]
                capacity = truck.get('capacity_lbs', 45000)
                utilization = (weight / capacity) * 100
                
                return {
                    'truck_id': truck['truck_id'],
                    'current_utilization': 0,
                    'new_utilization': utilization,
                    'remaining_capacity': capacity - weight,
                    'capacity_lbs': capacity,
                    'consolidation_possible': False,
                    'score': utilization
                }
            
            # Fallback: create virtual truck
            return {
                'truck_id': f'TRK-NEW-{np.random.randint(1000, 9999)}',
                'current_utilization': 0,
                'new_utilization': (weight / 45000) * 100,
                'remaining_capacity': 45000 - weight,
                'capacity_lbs': 45000,
                'consolidation_possible': False,
                'score': (weight / 45000) * 100
            }
    
    def calculate_route_metrics(self, source: str, destination: str, weight: float) -> Dict:
        """
        Calculate route distance, time, and costs
        """
        # Distance calculation (simplified - use Google Maps API in production)
        distance_km = self._estimate_distance(source, destination)
        distance_miles = distance_km * 0.621371
        
        # Travel time (assuming 60 km/h average)
        travel_hours = distance_km / 60
        travel_time = f"{int(travel_hours)}h {int((travel_hours % 1) * 60)}m"
        
        # Fuel consumption (6 MPG for loaded truck)
        fuel_gallons = distance_miles / 6.0
        fuel_cost = fuel_gallons * 3.50  # $3.50 per gallon
        
        # Driver cost ($25/hour)
        driver_cost = travel_hours * 25
        
        # Toll cost (estimated)
        toll_cost = distance_km * 0.05  # $0.05 per km
        
        # Total cost
        total_cost = fuel_cost + driver_cost + toll_cost
        
        # Carbon emissions (10.2 kg CO2 per gallon)
        emissions_kg = fuel_gallons * 10.2
        
        return {
            'distance_km': round(distance_km, 2),
            'distance_miles': round(distance_miles, 2),
            'travel_hours': round(travel_hours, 2),
            'travel_time': travel_time,
            'fuel_gallons': round(fuel_gallons, 2),
            'fuel_cost': round(fuel_cost, 2),
            'driver_cost': round(driver_cost, 2),
            'toll_cost': round(toll_cost, 2),
            'total_cost': round(total_cost, 2),
            'emissions_kg': round(emissions_kg, 2)
        }
    
    def _estimate_distance(self, source: str, destination: str) -> float:
        """
        Estimate distance between cities
        In production, use Google Maps Distance Matrix API
        """
        # Simplified distance estimation
        city_distances = {
            ('pune', 'mumbai'): 148,
            ('mumbai', 'pune'): 148,
            ('delhi', 'mumbai'): 1400,
            ('mumbai', 'delhi'): 1400,
            ('bangalore', 'chennai'): 346,
            ('chennai', 'bangalore'): 346,
            ('kolkata', 'delhi'): 1450,
            ('delhi', 'kolkata'): 1450,
        }
        
        key = (source.lower(), destination.lower())
        if key in city_distances:
            return city_distances[key]
        
        # Default estimate
        return 200 + np.random.randint(0, 300)
    
    def calculate_consolidation_savings(self, consolidation: bool, route_metrics: Dict) -> Dict:
        """
        Calculate cost savings from consolidation
        """
        if consolidation:
            # Savings = avoided new truck cost
            avoided_truck_cost = 500  # Daily truck cost
            fuel_savings = route_metrics['fuel_cost'] * 0.15  # 15% fuel efficiency gain
            total_savings = avoided_truck_cost + fuel_savings
            
            return {
                'consolidation_savings': round(total_savings, 2),
                'avoided_truck_cost': avoided_truck_cost,
                'fuel_savings': round(fuel_savings, 2),
                'savings_percentage': 40
            }
        else:
            return {
                'consolidation_savings': 0,
                'avoided_truck_cost': 0,
                'fuel_savings': 0,
                'savings_percentage': 0
            }
    
    def generate_dispatch_plan(self,
                               source: str,
                               destination: str,
                               weight: float,
                               priority: str = "medium",
                               delivery_date: str = None) -> Dict:
        """
        Main dispatch planning function
        Generates complete dispatch plan with all details
        """
        # Step 1: Find consolidation opportunities
        opportunities = self.find_consolidation_opportunities(source, destination, weight, priority)
        
        # Step 2: Select best truck
        selected_truck = self.select_best_truck(opportunities, weight)
        
        # Step 3: Calculate route metrics
        route_metrics = self.calculate_route_metrics(source, destination, weight)
        
        # Step 4: Calculate savings
        savings = self.calculate_consolidation_savings(
            selected_truck['consolidation_possible'],
            route_metrics
        )
        
        # Step 5: Generate complete dispatch plan
        dispatch_plan = {
            'dispatch_id': f'DISP-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'shipment_details': {
                'source': source,
                'destination': destination,
                'weight_lbs': weight,
                'weight_kg': round(weight * 0.453592, 2),
                'priority': priority,
                'delivery_date': delivery_date or (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            },
            'truck_assignment': {
                'truck_id': selected_truck['truck_id'],
                'truck_capacity_lbs': selected_truck['capacity_lbs'],
                'current_utilization_pct': round(selected_truck['current_utilization'], 2),
                'new_utilization_pct': round(selected_truck['new_utilization'], 2),
                'remaining_capacity_lbs': round(selected_truck['remaining_capacity'], 2),
                'consolidation_status': 'Consolidated' if selected_truck['consolidation_possible'] else 'New Allocation'
            },
            'route_details': route_metrics,
            'cost_analysis': {
                'fuel_cost': route_metrics['fuel_cost'],
                'driver_cost': route_metrics['driver_cost'],
                'toll_cost': route_metrics['toll_cost'],
                'total_cost': route_metrics['total_cost'],
                'cost_savings': savings['consolidation_savings'],
                'final_cost': round(route_metrics['total_cost'] - savings['consolidation_savings'], 2)
            },
            'environmental_impact': {
                'emissions_kg': route_metrics['emissions_kg'],
                'emissions_tons': round(route_metrics['emissions_kg'] / 1000, 3)
            },
            'optimization_score': round(selected_truck['score'], 2),
            'recommendations': self._generate_recommendations(selected_truck, route_metrics, savings)
        }
        
        return dispatch_plan
    
    def _generate_recommendations(self, truck: Dict, route: Dict, savings: Dict) -> List[str]:
        """Generate AI recommendations"""
        recommendations = []
        
        if truck['consolidation_possible']:
            recommendations.append(f"✓ Consolidation successful - saves ${savings['consolidation_savings']:.2f}")
            recommendations.append(f"✓ Truck utilization improved to {truck['new_utilization']:.1f}%")
        else:
            recommendations.append("→ New truck allocation required")
            if truck['new_utilization'] < 60:
                recommendations.append(f"⚠ Low utilization ({truck['new_utilization']:.1f}%) - consider combining with other shipments")
        
        if route['travel_hours'] > 8:
            recommendations.append("⚠ Long haul detected - consider driver rest requirements")
        
        if truck['new_utilization'] > 95:
            recommendations.append("✓ Excellent capacity utilization!")
        
        return recommendations
    
    def save_dispatch_plan(self, plan: Dict, output_dir: str = "dispatch/results"):
        """Save dispatch plan to file"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert numpy types to Python native types
        def convert_to_native(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_to_native(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            return obj
        
        plan_native = convert_to_native(plan)
        
        filename = f"{output_dir}/dispatch_{plan['dispatch_id']}.json"
        with open(filename, 'w') as f:
            json.dump(plan_native, f, indent=2)
        
        return filename


def create_dispatch_plan(source: str, destination: str, weight: float, 
                        priority: str = "medium", delivery_date: str = None) -> Dict:
    """
    Convenience function to create dispatch plan
    """
    dispatcher = SmartDispatcher()
    plan = dispatcher.generate_dispatch_plan(source, destination, weight, priority, delivery_date)
    return plan


if __name__ == "__main__":
    # Test dispatch planner
    print("="*80)
    print("SMART DISPATCH PLANNER - TEST")
    print("="*80)
    
    test_plan = create_dispatch_plan(
        source="Pune",
        destination="Mumbai",
        weight=1200,
        priority="high"
    )
    
    print(json.dumps(test_plan, indent=2))
