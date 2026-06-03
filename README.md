# 🚚 AI Load Consolidation & Logistics Intelligence Platform

An enterprise-grade AI-powered logistics dispatch and optimization platform featuring intelligent load consolidation, route optimization, demand forecasting, and real-time dispatch planning.

## 🌟 Key Features

### 1. **Smart Dispatch Planner** (Primary Feature)
- **Intelligent Truck Allocation**: AI-powered truck selection based on capacity, location, and availability
- **Consolidation Detection**: Automatically identifies opportunities to combine shipments
- **Route Optimization**: OR-Tools powered route calculation with distance, time, and cost analysis
- **Real-time Decision Engine**: Multi-factor optimization considering capacity, cost, distance, and delivery priority
- **Professional Dispatch Plans**: Generate comprehensive dispatch reports with all logistics metrics
- **Environmental Impact**: Track CO₂ emissions and sustainability metrics

### 2. **Load Consolidation Optimization**
- Advanced clustering algorithms for shipment grouping
- 35% truck utilization improvement
- 28.1% mileage reduction
- $306,084 annual cost savings

### 3. **Demand Forecasting**
- 30-day demand prediction using ARIMA
- 93.7% forecast accuracy
- Pattern detection for seasonal trends
- Capacity planning recommendations

### 4. **Route Intelligence**
- OR-Tools route optimization
- Multi-stop route planning
- Fuel cost calculation
- Real-time travel time estimation

### 5. **Emissions Analytics**
- Carbon footprint tracking
- 168.3 metric tons CO₂ saved annually
- Sustainability reporting
- Environmental compliance monitoring

### 6. **Interactive Dashboard**
- Real-time dispatch planning interface
- Executive analytics dashboard
- Interactive maps with Folium
- Comprehensive KPI tracking
- Multi-page Streamlit interface

### 7. **RESTful API**
- FastAPI backend with 15+ endpoints
- `/dispatch-plan` - Create intelligent dispatch plans
- `/optimize` - Run consolidation optimization
- `/forecast` - Generate demand forecasts
- Comprehensive API documentation

### 8. **AI Copilot**
- Natural language dispatch queries
- Explain optimization decisions
- Answer logistics questions
- Scenario analysis

## 📊 Platform Metrics

| Metric | Value | Improvement |
|--------|-------|-------------|
| **Trucks Saved** | 42 units | 35% reduction |
| **Miles Saved** | 128,760 miles | 28.1% reduction |
| **Annual Savings** | $306,084 | Cost optimization |
| **CO₂ Reduction** | 168.3 tons | Environmental impact |
| **Forecast Accuracy** | 93.7% | Demand prediction |
| **Data Coverage** | 574,706 records | Comprehensive analysis |

## 🏗️ Architecture

```
AI_LOAD_CONSOLIDATION_PROBLEM/
├── backend/                 # FastAPI REST API
│   └── main.py             # 15+ endpoints
├── dashboard/              # Streamlit Web UI
│   └── app.py             # 9-page dashboard
├── dispatch/              # Smart Dispatch Planner
│   ├── smart_dispatcher.py
│   └── results/
├── optimization/          # Consolidation Engine
│   ├── clustering.py
│   ├── consolidation.py
│   └── routing.py
├── forecasting/          # Demand Forecasting
│   └── demand_forecast.py
├── data_processing/      # Data Pipeline
│   ├── pipeline.py
│   ├── data_cleaner.py
│   └── data_analyzer.py
├── database/            # Database Schema
│   ├── dispatch_schema.sql
│   └── models.py
└── Dataset/            # Raw Data (15 datasets)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, for persistence)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/AI_LOAD_CONSOLIDATION_PROBLEM.git
cd AI_LOAD_CONSOLIDATION_PROBLEM
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run data processing pipeline** (first time only)
```bash
python data_processing/pipeline.py
```

6. **Start the backend API**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

7. **Start the dashboard** (in a new terminal)
```bash
streamlit run dashboard/app.py
```

8. **Access the platform**
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs

## 📱 Using the Smart Dispatch Planner

1. Navigate to **Smart Dispatch Planner** (first menu item)
2. Enter shipment details:
   - Source location
   - Destination location
   - Shipment weight (lbs)
   - Priority (Low/Medium/High/Critical)
   - Delivery date
3. Click **Create Dispatch Plan**
4. View comprehensive results:
   - **Summary**: Key metrics and consolidation status
   - **Truck Details**: Assigned vehicle and capacity utilization
   - **Route & Costs**: Distance, time, fuel, and total costs
   - **AI Insights**: Recommendations and decision explanations
5. Download dispatch plan as JSON

## 🔧 API Usage

### Create Dispatch Plan
```bash
curl -X POST "http://localhost:8000/dispatch-plan" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "Pune",
    "destination": "Mumbai",
    "weight": 12000,
    "priority": "high",
    "delivery_date": "2026-06-05"
  }'
```

### Response
```json
{
  "dispatch_id": "DISP-20260603114959",
  "truck_assignment": {
    "truck_id": "TRK00001",
    "truck_capacity": 45000,
    "current_utilization": 30000,
    "final_utilization": 42000,
    "utilization_percentage": 93.3,
    "consolidation_status": "Consolidated"
  },
  "route_plan": {
    "distance_km": 148.5,
    "travel_time_hours": 3.25,
    "estimated_arrival": "2026-06-05T14:30:00"
  },
  "cost_breakdown": {
    "fuel_cost": 2240.50,
    "driver_cost": 650.00,
    "toll_cost": 450.00,
    "total_cost": 3340.50
  },
  "savings": {
    "consolidation_savings": 2800.00,
    "efficiency_gain": "83%"
  }
}
```

## 📈 Data Processing Pipeline

The platform processes 15 datasets totaling 574,706 records:

1. **Data Cleaning**: 99.80% completeness after cleaning
2. **Feature Engineering**: 68 features across all datasets
3. **Unification**: 85,410 unified records
4. **Analysis**: Statistical profiling and quality checks

Datasets:
- Trucks, Trailers, Drivers
- Routes, Trips, Loads
- Facilities, Customers
- Fuel Purchases, Maintenance Records
- Safety Incidents, Delivery Events
- Utilization Metrics

## 🗄️ Database Schema

5 new dispatch-specific tables:
- `dispatch_plans`: Master dispatch records
- `truck_assignments`: Vehicle allocation history
- `route_recommendations`: Optimized route plans
- `consolidation_results`: Shipment grouping analysis
- `dispatch_history`: Audit trail

## 🐳 Docker Deployment

```bash
docker-compose up -d
```

Services:
- API: http://localhost:8000
- Dashboard: http://localhost:8501
- PostgreSQL: localhost:5432

## 📚 Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)**: Detailed setup guide
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**: Production deployment
- **[SMART_DISPATCH_UPDATE.md](SMART_DISPATCH_UPDATE.md)**: Dispatch planner documentation
- **API Docs**: http://localhost:8000/docs (when running)

## 🧪 Testing

```bash
# Test dispatch planner
python test_dispatch.py

# Test data pipeline
python data_processing/pipeline.py

# Test optimization
python optimization/consolidation.py
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit, Plotly, Folium
- **AI/ML**: scikit-learn, ARIMA, Prophet
- **Optimization**: OR-Tools, Google OR
- **Data**: Pandas, NumPy
- **Database**: PostgreSQL, SQLAlchemy
- **Deployment**: Docker, Docker Compose

## 📊 Dashboard Pages

1. **Smart Dispatch Planner** - Create and manage dispatch plans
2. **Executive Dashboard** - High-level KPIs and metrics
3. **Load Consolidation** - Optimization results and analysis
4. **Route Analytics** - Route performance and efficiency
5. **Demand Forecast** - Predictive analytics
6. **Fleet Management** - Truck and driver metrics
7. **Cost Analysis** - Financial breakdown and ROI
8. **Emissions Tracker** - Environmental impact
9. **AI Copilot** - Natural language assistant

## 🎯 Use Cases

- **Logistics Companies**: Optimize dispatch operations and reduce costs
- **Supply Chain Managers**: Improve efficiency and visibility
- **Transportation Planners**: Route optimization and capacity planning
- **Fleet Operators**: Vehicle utilization and maintenance planning
- **Sustainability Officers**: Carbon footprint tracking and reduction

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- **Your Name** - Initial work

## 🙏 Acknowledgments

- OR-Tools for route optimization
- Streamlit for the interactive dashboard
- FastAPI for the robust backend
- The open-source community

## 📞 Support

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for smarter logistics**
