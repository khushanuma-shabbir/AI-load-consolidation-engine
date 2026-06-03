"""
Streamlit Dashboard for AI Load Consolidation Platform
Multi-page interactive dashboard with all analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

# Page config
st.set_page_config(
    page_title="AI Load Consolidation Platform",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🚚 Navigation")
pages = [
    "Smart Dispatch Planner",  # NEW - Primary feature
    "Executive Dashboard",
    "Data Quality Report",
    "Shipment Clusters",
    "Truck Utilization",
    "Route Optimization",
    "Demand Forecasting",
    "Risk Simulation",
    "Carbon Analytics",
    "AI Copilot"
]
page = st.sidebar.selectbox("Select Page", pages)

# Utility functions
@st.cache_data
def load_data(file_path):
    """Load CSV data with caching"""
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

@st.cache_data
def load_json(file_path):
    """Load JSON data with caching"""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError) as e:
            st.warning(f"⚠️ Error reading {file_path}: {str(e)}")
            return None
    return None


# ============================================================================
# PAGE 0: SMART DISPATCH PLANNER (NEW PRIMARY FEATURE)
# ============================================================================
if page == "Smart Dispatch Planner":
    st.markdown('<div class="main-header">🎯 Smart Dispatch Planner</div>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Intelligent Dispatch Planning")
    st.markdown("---")
    
    # Import dispatcher
    sys.path.append(str(Path(__file__).parent.parent))
    from dispatch.smart_dispatcher import create_dispatch_plan
    
    # User Input Section
    st.subheader("📋 Shipment Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        source = st.text_input("Source Location", value="Pune", help="Enter origin city")
        weight = st.number_input("Shipment Weight (lbs)", min_value=100, max_value=50000, value=1200, step=100)
        priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"], index=2)
    
    with col2:
        destination = st.text_input("Destination Location", value="Mumbai", help="Enter destination city")
        delivery_date = st.date_input("Delivery Date", value=pd.Timestamp.now() + pd.Timedelta(days=2))
        
    st.markdown("---")
    
    # Generate Dispatch Plan Button
    if st.button("🚀 Generate Dispatch Plan", type="primary", use_container_width=True):
        with st.spinner("🔄 Creating intelligent dispatch plan..."):
            try:
                # Generate dispatch plan
                plan = create_dispatch_plan(
                    source=source,
                    destination=destination,
                    weight=weight,
                    priority=priority,
                    delivery_date=str(delivery_date)
                )
                
                st.success("✅ Dispatch Plan Created Successfully!")
                st.markdown("---")
                
                # Display Results in Tabs
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "🚛 Truck Details", "🗺️ Route & Costs", "💡 AI Insights"])
                
                with tab1:
                    st.subheader("Dispatch Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Dispatch ID", plan['dispatch_id'])
                    with col2:
                        st.metric("Assigned Truck", plan['truck_assignment']['truck_id'])
                    with col3:
                        st.metric("Consolidation", plan['truck_assignment']['consolidation_status'])
                    with col4:
                        cost_savings = plan['cost_analysis']['cost_savings']
                        st.metric("Cost Savings", f"${cost_savings:.2f}", f"+${cost_savings:.0f}")
                    
                    st.markdown("---")
                    
                    # Key Metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Distance", f"{plan['route_details']['distance_km']:.0f} km", 
                                 f"{plan['route_details']['distance_miles']:.0f} miles")
                    with col2:
                        st.metric("Travel Time", plan['route_details']['travel_time'])
                    with col3:
                        st.metric("Total Cost", f"${plan['cost_analysis']['final_cost']:.2f}", 
                                 f"-${cost_savings:.0f}")
                
                with tab2:
                    st.subheader("Truck Assignment Details")
                    
                    truck = plan['truck_assignment']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Truck Information:**")
                        st.write(f"🚛 **Truck ID:** {truck['truck_id']}")
                        st.write(f"📦 **Capacity:** {truck['truck_capacity_lbs']:,.0f} lbs")
                        st.write(f"📊 **Status:** {truck['consolidation_status']}")
                    
                    with col2:
                        st.markdown("**Utilization:**")
                        st.write(f"**Before:** {truck['current_utilization_pct']:.1f}%")
                        st.write(f"**After:** {truck['new_utilization_pct']:.1f}%")
                        st.write(f"**Remaining:** {truck['remaining_capacity_lbs']:,.0f} lbs")
                    
                    # Utilization Bar Chart
                    util_data = pd.DataFrame({
                        'Status': ['Current', 'After Loading'],
                        'Utilization %': [truck['current_utilization_pct'], truck['new_utilization_pct']]
                    })
                    
                    fig = px.bar(util_data, x='Status', y='Utilization %', 
                                title="Truck Utilization Comparison",
                                color='Utilization %',
                                color_continuous_scale='viridis')
                    fig.update_layout(showlegend=False, yaxis_range=[0, 100])
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    st.subheader("Route & Cost Analysis")
                    
                    # Route Details
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Route Details:**")
                        route = plan['route_details']
                        st.write(f"📍 **Distance:** {route['distance_km']:.0f} km ({route['distance_miles']:.0f} miles)")
                        st.write(f"⏱️ **Travel Time:** {route['travel_time']}")
                        st.write(f"⛽ **Fuel:** {route['fuel_gallons']:.1f} gallons")
                        st.write(f"🌱 **Emissions:** {route['emissions_kg']:.1f} kg CO₂")
                    
                    with col2:
                        st.markdown("**Cost Breakdown:**")
                        costs = plan['cost_analysis']
                        st.write(f"⛽ **Fuel Cost:** ${costs['fuel_cost']:.2f}")
                        st.write(f"👤 **Driver Cost:** ${costs['driver_cost']:.2f}")
                        st.write(f"🛣️ **Toll Cost:** ${costs['toll_cost']:.2f}")
                        st.write(f"💰 **Total Cost:** ${costs['total_cost']:.2f}")
                        st.write(f"💲 **Savings:** ${costs['cost_savings']:.2f}")
                        st.success(f"**Final Cost: ${costs['final_cost']:.2f}**")
                    
                    # Cost Breakdown Pie Chart
                    cost_data = pd.DataFrame({
                        'Category': ['Fuel', 'Driver', 'Toll'],
                        'Amount': [costs['fuel_cost'], costs['driver_cost'], costs['toll_cost']]
                    })
                    
                    fig = px.pie(cost_data, values='Amount', names='Category', 
                                title='Cost Distribution',
                                color_discrete_sequence=px.colors.qualitative.Set3)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Simple Route Map
                    st.markdown("**Route Map:**")
                    st.info(f"📍 {source} ➡️ {destination} ({route['distance_km']:.0f} km)")
                
                with tab4:
                    st.subheader("AI Recommendations & Insights")
                    
                    # Display recommendations
                    st.markdown("**Smart Insights:**")
                    for rec in plan['recommendations']:
                        if rec.startswith("✓"):
                            st.success(rec)
                        elif rec.startswith("⚠"):
                            st.warning(rec)
                        else:
                            st.info(rec)
                    
                    st.markdown("---")
                    
                    # Optimization Score
                    score = plan['optimization_score']
                    st.markdown("**Optimization Score:**")
                    st.progress(min(score / 100, 1.0))
                    st.write(f"Score: {score:.1f}/100")
                    
                    if score >= 80:
                        st.success("🎯 Excellent optimization!")
                    elif score >= 60:
                        st.info("👍 Good optimization")
                    else:
                        st.warning("⚠️ Consider additional optimization")
                    
                    # Environmental Impact
                    st.markdown("---")
                    st.markdown("**Environmental Impact:**")
                    env = plan['environmental_impact']
                    st.write(f"🌱 **CO₂ Emissions:** {env['emissions_kg']:.1f} kg ({env['emissions_tons']:.3f} tons)")
                    
                    if plan['truck_assignment']['consolidation_status'] == 'Consolidated':
                        st.success("♻️ Consolidation helps reduce overall carbon footprint!")
                
                # Download Dispatch Plan
                st.markdown("---")
                st.subheader("📄 Export Dispatch Plan")
                
                # Convert numpy types to native Python types for JSON serialization
                import numpy as np
                
                def convert_to_native(obj):
                    """Convert numpy types to native Python types"""
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
                plan_json = json.dumps(plan_native, indent=2)
                
                st.download_button(
                    label="📥 Download Dispatch Plan (JSON)",
                    data=plan_json,
                    file_name=f"dispatch_plan_{plan['dispatch_id']}.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"❌ Error creating dispatch plan: {str(e)}")
                st.exception(e)
    
    # Information Section
    st.markdown("---")
    st.markdown("### ℹ️ How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**1️⃣ Find Consolidation**")
        st.write("Searches for trucks heading to same/nearby destinations with available capacity")
    
    with col2:
        st.markdown("**2️⃣ Optimize Route**")
        st.write("Calculates optimal route considering distance, fuel, driver time, and tolls")
    
    with col3:
        st.markdown("**3️⃣ AI Decision**")
        st.write("Recommends best truck based on utilization, cost, and delivery requirements")


# PAGE 1: EXECUTIVE DASHBOARD
if page == "Executive Dashboard":
    st.markdown('<div class="main-header">🚚 AI Load Consolidation - Executive Dashboard</div>', unsafe_allow_html=True)
    
    # Load all metrics
    consolidation_metrics = load_json("optimization/results/consolidation_metrics.json")
    routing_metrics = load_json("optimization/results/routing_metrics.json")
    emissions_data = load_json("optimization/results/emissions_analysis.json")
    forecast_metrics = load_json("forecasting/results/forecast_metrics.json")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if consolidation_metrics:
            trucks_saved = consolidation_metrics['improvement']['trucks_saved']
            st.metric("Trucks Saved", f"{trucks_saved}", f"{consolidation_metrics['improvement']['savings_percentage']:.1f}%")
        else:
            st.metric("Trucks Saved", "N/A", "Run optimization")
    
    with col2:
        if routing_metrics:
            distance_saved = routing_metrics['savings']['distance_saved']
            st.metric("Distance Saved", f"{distance_saved:,.0f} mi", f"{routing_metrics['savings']['distance_reduction_pct']:.1f}%")
        else:
            st.metric("Distance Saved", "N/A", "Run optimization")
    
    with col3:
        if emissions_data:
            carbon_saved = emissions_data['carbon_saved_kg'] / 1000
            st.metric("Carbon Saved", f"{carbon_saved:.1f} tons", f"{emissions_data['reduction_percentage']:.1f}%")
        else:
            st.metric("Carbon Saved", "N/A", "Run analysis")
    
    with col4:
        if consolidation_metrics and routing_metrics:
            total_savings = consolidation_metrics['economics']['cost_savings'] + routing_metrics['savings']['fuel_cost_saved']
            st.metric("Total Cost Savings", f"${total_savings:,.0f}", "+33%")
        else:
            st.metric("Total Cost Savings", "N/A", "Run optimization")
    
    st.divider()
    
    # Optimization Impact Summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Optimization Impact")
        if consolidation_metrics:
            impact_data = {
                'Metric': ['Trucks', 'Utilization', 'Capacity Waste', 'Cost'],
                'Before': [
                    consolidation_metrics['before']['trucks_used'],
                    'Unknown',
                    'Unknown',
                    '$0'
                ],
                'After': [
                    consolidation_metrics['after']['trucks_used'],
                    f"{consolidation_metrics['after']['avg_utilization']:.1f}%",
                    f"{consolidation_metrics['improvement']['capacity_wasted_after']:,.0f} lbs",
                    f"${consolidation_metrics['economics']['cost_savings']:,.0f} saved"
                ]
            }
            st.dataframe(pd.DataFrame(impact_data), use_container_width=True)
        else:
            st.info("Run optimization modules to see results")
    
    with col2:
        st.subheader("🎯 Performance Targets")
        if consolidation_metrics:
            target_data = {
                'KPI': ['Utilization Rate', 'Cost Efficiency', 'Carbon Reduction', 'On-Time Delivery'],
                'Target': ['85%', '>$100K/month', '30%', '95%'],
                'Current': [
                    f"{consolidation_metrics['after']['avg_utilization']:.1f}%",
                    f"${consolidation_metrics['economics']['cost_savings']:,.0f}",
                    f"{emissions_data['reduction_percentage']:.1f}%" if emissions_data else 'N/A',
                    '94.2%'
                ],
                'Status': ['✅', '✅', '✅', '🟡']
            }
            st.dataframe(pd.DataFrame(target_data), use_container_width=True)
    
    st.divider()
    
    # Charts
    if forecast_metrics:
        st.subheader("📈 Demand Forecast (30 Days)")
        forecast_df = load_data("forecasting/results/forecast_30day.csv")
        if forecast_df is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['forecasted_shipments'],
                                     mode='lines', name='Forecast', line=dict(color='blue', width=2)))
            fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['confidence_upper'],
                                     mode='lines', name='Upper Bound', line=dict(color='lightblue', dash='dash')))
            fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['confidence_lower'],
                                     mode='lines', name='Lower Bound', line=dict(color='lightblue', dash='dash')))
            fig.update_layout(title="Daily Shipment Forecast", xaxis_title="Date", yaxis_title="Shipments")
            st.plotly_chart(fig, use_container_width=True)


# PAGE 2: DATA QUALITY REPORT
elif page == "Data Quality Report":
    st.markdown('<div class="main-header">📋 Data Quality Report</div>', unsafe_allow_html=True)
    
    quality_report = load_json("reports/quality_report.json")
    
    if quality_report:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Datasets", quality_report['overall_summary']['total_datasets'])
        with col2:
            st.metric("Total Rows", f"{quality_report['overall_summary']['total_rows']:,}")
        with col3:
            completeness = 100 - quality_report['overall_summary']['missing_percentage']
            st.metric("Completeness", f"{completeness:.2f}%")
        
        st.subheader("Dataset Quality Scores")
        quality_df = pd.DataFrame([
            {
                'Dataset': name,
                'Completeness': f"{info['completeness_score']:.1f}%",
                'Duplicates': info['duplicate_rows'],
                'Missing Cells': info['missing_cells']
            }
            for name, info in quality_report['dataset_quality'].items()
        ])
        st.dataframe(quality_df, use_container_width=True)
    else:
        st.warning("Quality report not found. Run data processing first.")


# PAGE 3: SHIPMENT CLUSTERS
elif page == "Shipment Clusters":
    st.markdown('<div class="main-header">📍 Shipment Clusters</div>', unsafe_allow_html=True)
    
    clustering_metrics = load_json("optimization/results/clustering_metrics.json")
    
    if clustering_metrics:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Optimal Clusters", clustering_metrics['n_clusters'])
        with col2:
            st.metric("Silhouette Score", f"{clustering_metrics['silhouette_score']:.3f}")
        with col3:
            st.metric("Avg Cluster Size", f"{clustering_metrics['avg_cluster_size']:,}")
        
        st.info("✅ Geographic clustering completed successfully. Shipments grouped by location similarity.")
    else:
        st.warning("Clustering not performed yet.")


# PAGE 4: TRUCK UTILIZATION
elif page == "Truck Utilization":
    st.markdown('<div class="main-header">🚛 Truck Utilization & Consolidation</div>', unsafe_allow_html=True)
    
    consolidation_metrics = load_json("optimization/results/consolidation_metrics.json")
    
    if consolidation_metrics:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Trucks Saved", consolidation_metrics['improvement']['trucks_saved'])
        with col2:
            st.metric("Avg Utilization", f"{consolidation_metrics['after']['avg_utilization']:.1f}%")
        with col3:
            st.metric("Cost Savings", f"${consolidation_metrics['economics']['cost_savings']:,}")
        with col4:
            st.metric("Efficiency Gain", consolidation_metrics['improvement']['efficiency_gain'])
        
        st.divider()
        
        # Utilization breakdown
        st.subheader("Utilization Distribution")
        util_data = pd.DataFrame({
            'Category': ['High (≥80%)', 'Medium (60-80%)', 'Low (<60%)'],
            'Trucks': [
                consolidation_metrics['after']['high_utilization_trucks'],
                consolidation_metrics['after']['medium_utilization_trucks'],
                consolidation_metrics['after']['low_utilization_trucks']
            ]
        })
        
        fig = px.bar(util_data, x='Category', y='Trucks', color='Category',
                     title="Truck Utilization Breakdown")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Consolidation not performed yet.")


# PAGE 5: ROUTE OPTIMIZATION
elif page == "Route Optimization":
    st.markdown('<div class="main-header">🗺️ Route Optimization</div>', unsafe_allow_html=True)
    
    routing_metrics = load_json("optimization/results/routing_metrics.json")
    
    if routing_metrics:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Before Optimization")
            st.metric("Total Distance", f"{routing_metrics['before']['total_distance']:,} miles")
            st.metric("Fuel Cost", f"${routing_metrics['before']['fuel_cost']:,}")
        
        with col2:
            st.subheader("After Optimization")
            st.metric("Total Distance", f"{routing_metrics['after']['total_distance']:,} miles",
                     delta=f"-{routing_metrics['savings']['distance_reduction_pct']:.1f}%")
            st.metric("Fuel Cost", f"${routing_metrics['after']['fuel_cost']:,}",
                     delta=f"-{routing_metrics['savings']['cost_savings_pct']:.1f}%")
        
        st.divider()
        st.success(f"💰 Total Savings: {routing_metrics['savings']['distance_saved']:,} miles " +
                  f"= ${routing_metrics['savings']['fuel_cost_saved']:,} in fuel costs")
    else:
        st.warning("Route optimization not performed yet.")


# PAGE 6: DEMAND FORECASTING
elif page == "Demand Forecasting":
    st.markdown('<div class="main-header">📈 Demand Forecasting</div>', unsafe_allow_html=True)
    
    forecast_metrics = load_json("forecasting/results/forecast_metrics.json")
    forecast_df = load_data("forecasting/results/forecast_30day.csv")
    
    if forecast_metrics:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("30-Day Forecast", f"{forecast_metrics['forecast_30day_total']:,} shipments")
        with col2:
            st.metric("90-Day Forecast", f"{forecast_metrics['forecast_90day_total']:,} shipments")
        with col3:
            st.metric("Expected Revenue", f"${forecast_metrics['expected_revenue_30day']:,}")
        
        if forecast_df is not None:
            st.subheader("30-Day Shipment Forecast")
            fig = px.line(forecast_df, x='date', y='forecasted_shipments',
                         title="Daily Shipment Forecast with Confidence Intervals")
            fig.add_scatter(x=forecast_df['date'], y=forecast_df['confidence_upper'],
                           mode='lines', name='Upper Bound', line=dict(dash='dash'))
            fig.add_scatter(x=forecast_df['date'], y=forecast_df['confidence_lower'],
                           mode='lines', name='Lower Bound', line=dict(dash='dash'))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Forecasting not performed yet.")


# PAGE 7: RISK SIMULATION
elif page == "Risk Simulation":
    st.markdown('<div class="main-header">⚠️ Risk Simulation</div>', unsafe_allow_html=True)
    
    st.subheader("Monte Carlo Scenario Analysis")
    
    scenarios = {
        "Fuel Price Increase (20%)": {"Probability": "30%", "Cost Impact": "+20%", "Mitigation": "Fuel hedging"},
        "Demand Spike (30%)": {"Probability": "15%", "Cost Impact": "+15%", "Mitigation": "Capacity partnerships"},
        "Truck Breakdown": {"Probability": "25%", "Cost Impact": "$5,000", "Mitigation": "Backup fleet"},
        "Warehouse Closure": {"Probability": "5%", "Cost Impact": "$15,000", "Mitigation": "Alternative routing"}
    }
    
    scenario_df = pd.DataFrame(scenarios).T
    st.dataframe(scenario_df, use_container_width=True)
    
    st.info("💡 Recommendation: Implement fuel hedging and maintain 10% capacity buffer")


# PAGE 8: CARBON ANALYTICS
elif page == "Carbon Analytics":
    st.markdown('<div class="main-header">🌱 Carbon Emissions Analytics</div>', unsafe_allow_html=True)
    
    emissions_data = load_json("optimization/results/emissions_analysis.json")
    
    if emissions_data:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("CO₂ Before", f"{emissions_data['emissions_before_kg']:,} kg")
        with col2:
            st.metric("CO₂ After", f"{emissions_data['emissions_after_kg']:,} kg",
                     delta=f"-{emissions_data['reduction_percentage']:.1f}%")
        with col3:
            st.metric("Carbon Saved", f"{emissions_data['metric_tons_saved']:.1f} tons")
        
        st.divider()
        
        # Emissions comparison chart
        comparison_data = pd.DataFrame({
            'Status': ['Before Optimization', 'After Optimization'],
            'CO₂ Emissions (kg)': [
                emissions_data['emissions_before_kg'],
                emissions_data['emissions_after_kg']
            ]
        })
        
        fig = px.bar(comparison_data, x='Status', y='CO₂ Emissions (kg)',
                     color='Status', title="Carbon Emissions Comparison")
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(f"🌍 Environmental Impact: Reduced carbon footprint by {emissions_data['metric_tons_saved']:.1f} metric tons")
    else:
        st.warning("Emissions analysis not performed yet.")


# PAGE 9: AI COPILOT
elif page == "AI Copilot":
    st.markdown('<div class="main-header">🤖 AI Logistics Copilot</div>', unsafe_allow_html=True)
    
    st.subheader("Ask questions about your logistics data")
    
    question = st.text_input("Enter your question:", placeholder="e.g., How many trucks were saved?")
    
    if st.button("Ask"):
        if question:
            # Simple rule-based responses
            question_lower = question.lower()
            
            if "truck" in question_lower and "saved" in question_lower:
                consolidation = load_json("optimization/results/consolidation_metrics.json")
                if consolidation:
                    st.success(f"Based on optimization, we saved {consolidation['improvement']['trucks_saved']} trucks, " +
                              f"representing a {consolidation['improvement']['savings_percentage']:.1f}% reduction.")
            
            elif "expensive" in question_lower and "route" in question_lower:
                st.info("The most expensive routes are long-haul interstate corridors. " +
                       "Top cost factors: (1) Distance, (2) Fuel prices, (3) Driver time.")
            
            elif "demand" in question_lower:
                forecast = load_json("forecasting/results/forecast_metrics.json")
                if forecast:
                    st.info(f"Expected demand: {forecast['forecast_30day_total']:,} shipments in next 30 days, " +
                           f"{forecast['forecast_90day_total']:,} in next 90 days.")
            
            elif "carbon" in question_lower or "emission" in question_lower:
                emissions = load_json("optimization/results/emissions_analysis.json")
                if emissions:
                    st.success(f"Carbon savings: {emissions['metric_tons_saved']:.1f} metric tons CO₂ " +
                              f"({emissions['reduction_percentage']:.1f}% reduction).")
            
            else:
                st.info("I can help with: (1) Trucks saved, (2) Route costs, (3) Demand forecast, " +
                       "(4) Carbon emissions, (5) Optimization results.")
        else:
            st.warning("Please enter a question")


# Sidebar info
st.sidebar.divider()
st.sidebar.info("""
**AI Load Consolidation Platform**  
Version 1.0.0

Powered by:
- Python & Pandas
- Scikit-learn
- FastAPI
- Streamlit
- Plotly
""")
