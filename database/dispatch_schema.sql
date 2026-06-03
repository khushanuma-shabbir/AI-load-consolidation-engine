-- Smart Dispatch Planner Database Schema
-- PostgreSQL DDL for dispatch planning tables

-- ============================================================================
-- TABLE: dispatch_plans
-- Stores all created dispatch plans
-- ============================================================================
CREATE TABLE IF NOT EXISTS dispatch_plans (
    dispatch_id VARCHAR(50) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_location VARCHAR(100) NOT NULL,
    destination_location VARCHAR(100) NOT NULL,
    shipment_weight_lbs DECIMAL(10, 2) NOT NULL,
    shipment_weight_kg DECIMAL(10, 2),
    priority VARCHAR(20) DEFAULT 'medium',
    delivery_date DATE,
    assigned_truck_id VARCHAR(50) NOT NULL,
    consolidation_status VARCHAR(50),
    optimization_score DECIMAL(5, 2),
    total_cost DECIMAL(10, 2),
    cost_savings DECIMAL(10, 2),
    final_cost DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'planned',
    
    INDEX idx_created_at (created_at),
    INDEX idx_truck (assigned_truck_id),
    INDEX idx_status (status),
    INDEX idx_delivery_date (delivery_date)
);

-- ============================================================================
-- TABLE: truck_assignments
-- Tracks truck assignments for each dispatch
-- ============================================================================
CREATE TABLE IF NOT EXISTS truck_assignments (
    assignment_id SERIAL PRIMARY KEY,
    dispatch_id VARCHAR(50) REFERENCES dispatch_plans(dispatch_id),
    truck_id VARCHAR(50) NOT NULL,
    truck_capacity_lbs DECIMAL(10, 2),
    current_utilization_pct DECIMAL(5, 2),
    new_utilization_pct DECIMAL(5, 2),
    remaining_capacity_lbs DECIMAL(10, 2),
    consolidation_possible BOOLEAN DEFAULT FALSE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_dispatch (dispatch_id),
    INDEX idx_truck (truck_id),
    INDEX idx_assigned_at (assigned_at)
);

-- ============================================================================
-- TABLE: route_recommendations
-- Stores route details and optimization results
-- ============================================================================
CREATE TABLE IF NOT EXISTS route_recommendations (
    route_id SERIAL PRIMARY KEY,
    dispatch_id VARCHAR(50) REFERENCES dispatch_plans(dispatch_id),
    source VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    distance_km DECIMAL(10, 2),
    distance_miles DECIMAL(10, 2),
    travel_hours DECIMAL(5, 2),
    travel_time VARCHAR(50),
    fuel_gallons DECIMAL(8, 2),
    fuel_cost DECIMAL(10, 2),
    driver_cost DECIMAL(10, 2),
    toll_cost DECIMAL(10, 2),
    total_route_cost DECIMAL(10, 2),
    emissions_kg DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_dispatch (dispatch_id),
    INDEX idx_source_dest (source, destination),
    INDEX idx_created_at (created_at)
);

-- ============================================================================
-- TABLE: consolidation_results
-- Tracks consolidation opportunities and outcomes
-- ============================================================================
CREATE TABLE IF NOT EXISTS consolidation_results (
    consolidation_id SERIAL PRIMARY KEY,
    dispatch_id VARCHAR(50) REFERENCES dispatch_plans(dispatch_id),
    truck_id VARCHAR(50) NOT NULL,
    consolidation_achieved BOOLEAN DEFAULT FALSE,
    utilization_improvement DECIMAL(5, 2),
    cost_savings DECIMAL(10, 2),
    fuel_savings DECIMAL(8, 2),
    avoided_truck_cost DECIMAL(10, 2),
    savings_percentage DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_dispatch (dispatch_id),
    INDEX idx_truck (truck_id),
    INDEX idx_consolidation (consolidation_achieved),
    INDEX idx_created_at (created_at)
);

-- ============================================================================
-- TABLE: dispatch_history
-- Audit log for all dispatch operations
-- ============================================================================
CREATE TABLE IF NOT EXISTS dispatch_history (
    history_id SERIAL PRIMARY KEY,
    dispatch_id VARCHAR(50) REFERENCES dispatch_plans(dispatch_id),
    action VARCHAR(50) NOT NULL,  -- created, updated, assigned, completed, cancelled
    performed_by VARCHAR(100),
    action_details TEXT,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_dispatch (dispatch_id),
    INDEX idx_action (action),
    INDEX idx_timestamp (action_timestamp)
);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Active Dispatches View
CREATE OR REPLACE VIEW active_dispatches AS
SELECT 
    dp.*,
    ta.truck_id,
    ta.new_utilization_pct,
    ta.consolidation_possible,
    rr.distance_km,
    rr.travel_time,
    rr.total_route_cost,
    cr.cost_savings
FROM dispatch_plans dp
LEFT JOIN truck_assignments ta ON dp.dispatch_id = ta.dispatch_id
LEFT JOIN route_recommendations rr ON dp.dispatch_id = rr.dispatch_id
LEFT JOIN consolidation_results cr ON dp.dispatch_id = cr.dispatch_id
WHERE dp.status IN ('planned', 'assigned', 'in_transit')
ORDER BY dp.created_at DESC;

-- Consolidation Summary View
CREATE OR REPLACE VIEW consolidation_summary AS
SELECT 
    COUNT(*) as total_dispatches,
    SUM(CASE WHEN consolidation_achieved THEN 1 ELSE 0 END) as consolidated_count,
    ROUND(AVG(utilization_improvement), 2) as avg_utilization_gain,
    ROUND(SUM(cost_savings), 2) as total_cost_savings,
    ROUND(AVG(cost_savings), 2) as avg_cost_savings_per_dispatch,
    ROUND(AVG(savings_percentage), 2) as avg_savings_percentage
FROM consolidation_results
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days';

-- Truck Utilization View
CREATE OR REPLACE VIEW truck_utilization_by_dispatch AS
SELECT 
    ta.truck_id,
    COUNT(DISTINCT ta.dispatch_id) as dispatch_count,
    ROUND(AVG(ta.new_utilization_pct), 2) as avg_utilization,
    ROUND(MIN(ta.new_utilization_pct), 2) as min_utilization,
    ROUND(MAX(ta.new_utilization_pct), 2) as max_utilization,
    SUM(CASE WHEN ta.consolidation_possible THEN 1 ELSE 0 END) as consolidation_count
FROM truck_assignments ta
GROUP BY ta.truck_id
ORDER BY avg_utilization DESC;

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_dispatch_status_date ON dispatch_plans(status, delivery_date);
CREATE INDEX IF NOT EXISTS idx_truck_consolidation ON truck_assignments(truck_id, consolidation_possible);
CREATE INDEX IF NOT EXISTS idx_route_distance ON route_recommendations(distance_km);

-- ============================================================================
-- SAMPLE DATA INSERTS (for testing)
-- ============================================================================

-- Sample dispatch plan
INSERT INTO dispatch_plans 
(dispatch_id, source_location, destination_location, shipment_weight_lbs, shipment_weight_kg, 
 priority, delivery_date, assigned_truck_id, consolidation_status, optimization_score, 
 total_cost, cost_savings, final_cost, status)
VALUES 
('DISP-20260603120000', 'Pune', 'Mumbai', 1200, 544.31, 'high', '2026-06-05', 
 'TRK-00025', 'Consolidated', 85.5, 850.50, 340.20, 510.30, 'planned')
ON CONFLICT (dispatch_id) DO NOTHING;

-- Sample truck assignment
INSERT INTO truck_assignments 
(dispatch_id, truck_id, truck_capacity_lbs, current_utilization_pct, 
 new_utilization_pct, remaining_capacity_lbs, consolidation_possible)
VALUES 
('DISP-20260603120000', 'TRK-00025', 45000, 65.0, 85.5, 6525, TRUE)
ON CONFLICT DO NOTHING;

-- Sample route recommendation
INSERT INTO route_recommendations 
(dispatch_id, source, destination, distance_km, distance_miles, travel_hours, 
 travel_time, fuel_gallons, fuel_cost, driver_cost, toll_cost, total_route_cost, emissions_kg)
VALUES 
('DISP-20260603120000', 'Pune', 'Mumbai', 148, 92, 3.25, '3h 15m', 
 15.3, 53.55, 81.25, 7.40, 142.20, 156.06)
ON CONFLICT DO NOTHING;

-- Sample consolidation result
INSERT INTO consolidation_results 
(dispatch_id, truck_id, consolidation_achieved, utilization_improvement, 
 cost_savings, fuel_savings, avoided_truck_cost, savings_percentage)
VALUES 
('DISP-20260603120000', 'TRK-00025', TRUE, 20.5, 340.20, 40.20, 300.00, 40.0)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- GRANT PERMISSIONS (adjust as needed)
-- ============================================================================

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO logistics_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO logistics_user;

-- ============================================================================
-- NOTES
-- ============================================================================

-- 1. Run this schema on PostgreSQL 12+
-- 2. Adjust VARCHAR lengths based on your data requirements
-- 3. Add additional indexes based on query patterns
-- 4. Implement partitioning for large-scale deployments
-- 5. Set up regular VACUUM and ANALYZE jobs
-- 6. Configure proper backup and replication
-- 7. Monitor query performance and optimize indexes

-- To execute this schema:
-- psql -U postgres -d logistics -f dispatch_schema.sql
