"""
AI MODULE 5: Demand Forecasting
Time series forecasting using statistical models
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class DemandForecaster:
    """Demand forecasting using time series analysis"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.forecasts = {}
        self.metrics = {}
        
    def prepare_time_series(self) -> pd.DataFrame:
        """
        Prepare time series data for forecasting
        """
        # Find date columns
        date_cols = [col for col in self.data.columns if 'date' in col.lower()]
        
        if not date_cols:
            print("Warning: No date columns found, creating synthetic dates")
            self.data['date'] = pd.date_range(start='2023-01-01', periods=len(self.data), freq='D')
            date_col = 'date'
        else:
            date_col = date_cols[0]
            self.data[date_col] = pd.to_datetime(self.data[date_col], errors='coerce')
        
        # Aggregate by date
        ts_data = self.data.groupby(pd.Grouper(key=date_col, freq='D')).agg({
            'load_id': 'count' if 'load_id' in self.data.columns else lambda x: len(x),
            'revenue': 'sum' if 'revenue' in self.data.columns else lambda x: 0,
            'weight': 'sum' if 'weight' in self.data.columns else lambda x: 0
        }).reset_index()
        
        ts_data.columns = ['date', 'shipment_count', 'total_revenue', 'total_weight']
        ts_data = ts_data.sort_values('date')
        
        return ts_data
    
    def simple_moving_average(self, series: pd.Series, window: int = 7) -> pd.Series:
        """
        Calculate simple moving average
        """
        return series.rolling(window=window, min_periods=1).mean()
    
    def exponential_smoothing(self, series: pd.Series, alpha: float = 0.3) -> pd.Series:
        """
        Exponential smoothing forecast
        """
        result = [series.iloc[0]]
        for i in range(1, len(series)):
            result.append(alpha * series.iloc[i] + (1 - alpha) * result[-1])
        return pd.Series(result, index=series.index)
    
    def forecast_demand(self, forecast_days: int = 30):
        """
        Forecast demand for next N days
        """
        print("="*80)
        print("DEMAND FORECASTING")
        print("="*80)
        
        # Prepare time series
        print("\nPreparing time series data...")
        ts_data = self.prepare_time_series()
        print(f"✓ Time series prepared: {len(ts_data)} days of data")
        
        # Forecast shipment count
        print("\nForecasting shipment demand...")
        shipment_series = ts_data['shipment_count']
        
        # Calculate trend
        recent_avg = shipment_series.tail(30).mean()
        overall_avg = shipment_series.mean()
        trend_factor = recent_avg / overall_avg if overall_avg > 0 else 1.0
        
        # Generate forecast
        last_date = ts_data['date'].max()
        forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days, freq='D')
        
        # Simple forecast: recent average + trend + seasonality
        base_forecast = recent_avg * trend_factor
        seasonal_pattern = [1.0, 1.05, 1.1, 1.0, 0.95, 0.8, 0.85]  # Weekly pattern
        
        forecasted_shipments = []
        forecasted_revenue = []
        forecasted_weight = []
        
        avg_revenue_per_shipment = ts_data['total_revenue'].sum() / ts_data['shipment_count'].sum() if ts_data['shipment_count'].sum() > 0 else 1000
        avg_weight_per_shipment = ts_data['total_weight'].sum() / ts_data['shipment_count'].sum() if ts_data['shipment_count'].sum() > 0 else 5000
        
        for i, date in enumerate(forecast_dates):
            day_of_week = date.dayofweek
            seasonal_adj = seasonal_pattern[day_of_week]
            noise = np.random.normal(1.0, 0.1)
            
            shipment_forecast = base_forecast * seasonal_adj * noise
            forecasted_shipments.append(max(0, int(shipment_forecast)))
            forecasted_revenue.append(forecasted_shipments[-1] * avg_revenue_per_shipment)
            forecasted_weight.append(forecasted_shipments[-1] * avg_weight_per_shipment)
        
        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'forecasted_shipments': forecasted_shipments,
            'forecasted_revenue': forecasted_revenue,
            'forecasted_weight': forecasted_weight,
            'confidence_lower': [int(s * 0.8) for s in forecasted_shipments],
            'confidence_upper': [int(s * 1.2) for s in forecasted_shipments]
        })
        
        self.forecasts['30_day'] = forecast_df.head(30)
        self.forecasts['90_day'] = pd.concat([
            forecast_df.head(30),
            pd.DataFrame({
                'date': pd.date_range(start=forecast_dates[29] + timedelta(days=1), periods=60, freq='D'),
                'forecasted_shipments': [int(base_forecast * np.random.normal(1.0, 0.15)) for _ in range(60)],
                'forecasted_revenue': [base_forecast * avg_revenue_per_shipment * np.random.normal(1.0, 0.15) for _ in range(60)],
                'forecasted_weight': [base_forecast * avg_weight_per_shipment * np.random.normal(1.0, 0.15) for _ in range(60)],
                'confidence_lower': [int(base_forecast * 0.7) for _ in range(60)],
                'confidence_upper': [int(base_forecast * 1.3) for _ in range(60)]
            })
        ])
        
        # Calculate metrics
        self.metrics = {
            'historical_avg_daily_shipments': float(shipment_series.mean()),
            'recent_avg_daily_shipments': float(recent_avg),
            'trend_factor': float(trend_factor),
            'forecast_30day_avg': float(self.forecasts['30_day']['forecasted_shipments'].mean()),
            'forecast_30day_total': int(self.forecasts['30_day']['forecasted_shipments'].sum()),
            'forecast_90day_total': int(self.forecasts['90_day']['forecasted_shipments'].sum()),
            'expected_revenue_30day': float(self.forecasts['30_day']['forecasted_revenue'].sum()),
            'expected_revenue_90day': float(self.forecasts['90_day']['forecasted_revenue'].sum())
        }
        
        print(f"\n✓ Forecast complete!")
        print(f"\nHISTORICAL METRICS:")
        print(f"  Historical Avg: {self.metrics['historical_avg_daily_shipments']:.1f} shipments/day")
        print(f"  Recent Avg (30d): {self.metrics['recent_avg_daily_shipments']:.1f} shipments/day")
        print(f"  Trend Factor: {self.metrics['trend_factor']:.2f}")
        print(f"\n30-DAY FORECAST:")
        print(f"  Expected Shipments: {self.metrics['forecast_30day_total']:,}")
        print(f"  Expected Revenue: ${self.metrics['expected_revenue_30day']:,.2f}")
        print(f"\n90-DAY FORECAST:")
        print(f"  Expected Shipments: {self.metrics['forecast_90day_total']:,}")
        print(f"  Expected Revenue: ${self.metrics['expected_revenue_90day']:,.2f}")
        
        return self.forecasts
    
    def save_results(self, output_dir: str = "forecasting/results"):
        """
        Save forecasting results
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save forecasts
        self.forecasts['30_day'].to_csv(f"{output_dir}/forecast_30day.csv", index=False)
        self.forecasts['90_day'].to_csv(f"{output_dir}/forecast_90day.csv", index=False)
        
        # Save metrics
        with open(f"{output_dir}/forecast_metrics.json", 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"\n✓ Forecasting results saved to {output_dir}/")


def run_forecasting(data_path: str = "processed_data/unified_logistics_dataset.csv"):
    """
    Main function to run demand forecasting
    """
    print("\n" + "="*80)
    print("AI MODULE 5: DEMAND FORECASTING")
    print("="*80)
    
    # Load data
    print("\nLoading data...")
    data = pd.read_csv(data_path)
    print(f"✓ Loaded {len(data):,} records")
    
    # Initialize forecaster
    forecaster = DemandForecaster(data)
    
    # Run forecasting
    forecasts = forecaster.forecast_demand(forecast_days=30)
    
    # Save results
    forecaster.save_results()
    
    print("\n✓ Demand forecasting complete!")
    
    return forecaster


if __name__ == "__main__":
    run_forecasting()
