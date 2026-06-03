"""
SQLAlchemy Models for Smart Dispatch Planner
ORM models for database interaction
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class DispatchPlan(Base):
    """Main dispatch plan record"""
    __tablename__ = 'dispatch_plans'
    
    dispatch_id = Column(String(50), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    source_location = Column(String(100), nullable=False)
    destination_location = Column(String(100), nullable=False)
    shipment_weight_lbs = Column(Float, nullable=False)
    shipment_weight_kg = Column(Float)
    priority = Column(String(20), default='medium')
    delivery_date = Column(Date)
    assigned_truck_id = Column(String(50), nullable=False)
    consolidation_status = Column(String(50))
    optimization_score = Column(Float)
    total_cost = Column(Float)
    cost_savings = Column(Float)
    final_cost = Column(Float)
    status = Column(String(20), default='planned')
    
    # Relationships
    truck_assignment = relationship("TruckAssignment", back_populates="dispatch_plan", uselist=False)
    route_recommendation = relationship("RouteRecommendation", back_populates="dispatch_plan", uselist=False)
    consolidation_result = relationship("ConsolidationResult", back_populates="dispatch_plan", uselist=False)
    history = relationship("DispatchHistory", back_populates="dispatch_plan")
    
    def to_dict(self):
        return {
            'dispatch_id': self.dispatch_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'source_location': self.source_location,
            'destination_location': self.destination_location,
            'shipment_weight_lbs': self.shipment_weight_lbs,
            'priority': self.priority,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'assigned_truck_id': self.assigned_truck_id,
            'consolidation_status': self.consolidation_status,
            'optimization_score': self.optimization_score,
            'total_cost': self.total_cost,
            'cost_savings': self.cost_savings,
            'final_cost': self.final_cost,
            'status': self.status
        }


class TruckAssignment(Base):
    """Truck assignment details"""
    __tablename__ = 'truck_assignments'
    
    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    dispatch_id = Column(String(50), ForeignKey('dispatch_plans.dispatch_id'))
    truck_id = Column(String(50), nullable=False)
    truck_capacity_lbs = Column(Float)
    current_utilization_pct = Column(Float)
    new_utilization_pct = Column(Float)
    remaining_capacity_lbs = Column(Float)
    consolidation_possible = Column(Boolean, default=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dispatch_plan = relationship("DispatchPlan", back_populates="truck_assignment")
    
    def to_dict(self):
        return {
            'assignment_id': self.assignment_id,
            'dispatch_id': self.dispatch_id,
            'truck_id': self.truck_id,
            'truck_capacity_lbs': self.truck_capacity_lbs,
            'current_utilization_pct': self.current_utilization_pct,
            'new_utilization_pct': self.new_utilization_pct,
            'remaining_capacity_lbs': self.remaining_capacity_lbs,
            'consolidation_possible': self.consolidation_possible,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None
        }


class RouteRecommendation(Base):
    """Route details and costs"""
    __tablename__ = 'route_recommendations'
    
    route_id = Column(Integer, primary_key=True, autoincrement=True)
    dispatch_id = Column(String(50), ForeignKey('dispatch_plans.dispatch_id'))
    source = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    distance_km = Column(Float)
    distance_miles = Column(Float)
    travel_hours = Column(Float)
    travel_time = Column(String(50))
    fuel_gallons = Column(Float)
    fuel_cost = Column(Float)
    driver_cost = Column(Float)
    toll_cost = Column(Float)
    total_route_cost = Column(Float)
    emissions_kg = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dispatch_plan = relationship("DispatchPlan", back_populates="route_recommendation")
    
    def to_dict(self):
        return {
            'route_id': self.route_id,
            'dispatch_id': self.dispatch_id,
            'source': self.source,
            'destination': self.destination,
            'distance_km': self.distance_km,
            'distance_miles': self.distance_miles,
            'travel_hours': self.travel_hours,
            'travel_time': self.travel_time,
            'fuel_gallons': self.fuel_gallons,
            'fuel_cost': self.fuel_cost,
            'driver_cost': self.driver_cost,
            'toll_cost': self.toll_cost,
            'total_route_cost': self.total_route_cost,
            'emissions_kg': self.emissions_kg,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ConsolidationResult(Base):
    """Consolidation outcomes and savings"""
    __tablename__ = 'consolidation_results'
    
    consolidation_id = Column(Integer, primary_key=True, autoincrement=True)
    dispatch_id = Column(String(50), ForeignKey('dispatch_plans.dispatch_id'))
    truck_id = Column(String(50), nullable=False)
    consolidation_achieved = Column(Boolean, default=False)
    utilization_improvement = Column(Float)
    cost_savings = Column(Float)
    fuel_savings = Column(Float)
    avoided_truck_cost = Column(Float)
    savings_percentage = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dispatch_plan = relationship("DispatchPlan", back_populates="consolidation_result")
    
    def to_dict(self):
        return {
            'consolidation_id': self.consolidation_id,
            'dispatch_id': self.dispatch_id,
            'truck_id': self.truck_id,
            'consolidation_achieved': self.consolidation_achieved,
            'utilization_improvement': self.utilization_improvement,
            'cost_savings': self.cost_savings,
            'fuel_savings': self.fuel_savings,
            'avoided_truck_cost': self.avoided_truck_cost,
            'savings_percentage': self.savings_percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DispatchHistory(Base):
    """Audit log for dispatch operations"""
    __tablename__ = 'dispatch_history'
    
    history_id = Column(Integer, primary_key=True, autoincrement=True)
    dispatch_id = Column(String(50), ForeignKey('dispatch_plans.dispatch_id'))
    action = Column(String(50), nullable=False)  # created, updated, assigned, completed, cancelled
    performed_by = Column(String(100))
    action_details = Column(Text)
    action_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dispatch_plan = relationship("DispatchPlan", back_populates="history")
    
    def to_dict(self):
        return {
            'history_id': self.history_id,
            'dispatch_id': self.dispatch_id,
            'action': self.action,
            'performed_by': self.performed_by,
            'action_details': self.action_details,
            'action_timestamp': self.action_timestamp.isoformat() if self.action_timestamp else None
        }


# Database connection utilities
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

def get_database_url():
    """Get database URL from environment or use default"""
    return os.getenv('DATABASE_URL', 'postgresql://admin:admin123@localhost:5432/logistics')

def create_db_engine():
    """Create database engine"""
    database_url = get_database_url()
    engine = create_engine(database_url, echo=False)
    return engine

def get_session():
    """Get database session"""
    engine = create_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_database():
    """Initialize database with all tables"""
    engine = create_db_engine()
    Base.metadata.create_all(engine)
    print("✓ Database tables created successfully")

def save_dispatch_to_db(dispatch_plan: dict):
    """
    Save dispatch plan to database
    """
    session = get_session()
    
    try:
        # Create main dispatch plan record
        dp = DispatchPlan(
            dispatch_id=dispatch_plan['dispatch_id'],
            source_location=dispatch_plan['shipment_details']['source'],
            destination_location=dispatch_plan['shipment_details']['destination'],
            shipment_weight_lbs=dispatch_plan['shipment_details']['weight_lbs'],
            shipment_weight_kg=dispatch_plan['shipment_details']['weight_kg'],
            priority=dispatch_plan['shipment_details']['priority'],
            delivery_date=datetime.strptime(dispatch_plan['shipment_details']['delivery_date'], '%Y-%m-%d').date(),
            assigned_truck_id=dispatch_plan['truck_assignment']['truck_id'],
            consolidation_status=dispatch_plan['truck_assignment']['consolidation_status'],
            optimization_score=dispatch_plan['optimization_score'],
            total_cost=dispatch_plan['cost_analysis']['total_cost'],
            cost_savings=dispatch_plan['cost_analysis']['cost_savings'],
            final_cost=dispatch_plan['cost_analysis']['final_cost'],
            status='planned'
        )
        session.add(dp)
        
        # Create truck assignment record
        ta = TruckAssignment(
            dispatch_id=dispatch_plan['dispatch_id'],
            truck_id=dispatch_plan['truck_assignment']['truck_id'],
            truck_capacity_lbs=dispatch_plan['truck_assignment']['truck_capacity_lbs'],
            current_utilization_pct=dispatch_plan['truck_assignment']['current_utilization_pct'],
            new_utilization_pct=dispatch_plan['truck_assignment']['new_utilization_pct'],
            remaining_capacity_lbs=dispatch_plan['truck_assignment']['remaining_capacity_lbs'],
            consolidation_possible=dispatch_plan['truck_assignment']['consolidation_status'] == 'Consolidated'
        )
        session.add(ta)
        
        # Create route recommendation record
        rr = RouteRecommendation(
            dispatch_id=dispatch_plan['dispatch_id'],
            source=dispatch_plan['shipment_details']['source'],
            destination=dispatch_plan['shipment_details']['destination'],
            distance_km=dispatch_plan['route_details']['distance_km'],
            distance_miles=dispatch_plan['route_details']['distance_miles'],
            travel_hours=dispatch_plan['route_details']['travel_hours'],
            travel_time=dispatch_plan['route_details']['travel_time'],
            fuel_gallons=dispatch_plan['route_details']['fuel_gallons'],
            fuel_cost=dispatch_plan['route_details']['fuel_cost'],
            driver_cost=dispatch_plan['route_details']['driver_cost'],
            toll_cost=dispatch_plan['route_details']['toll_cost'],
            total_route_cost=dispatch_plan['route_details']['total_cost'],
            emissions_kg=dispatch_plan['route_details']['emissions_kg']
        )
        session.add(rr)
        
        # Create consolidation result record
        cr = ConsolidationResult(
            dispatch_id=dispatch_plan['dispatch_id'],
            truck_id=dispatch_plan['truck_assignment']['truck_id'],
            consolidation_achieved=dispatch_plan['truck_assignment']['consolidation_status'] == 'Consolidated',
            cost_savings=dispatch_plan['cost_analysis']['cost_savings']
        )
        session.add(cr)
        
        # Create history record
        dh = DispatchHistory(
            dispatch_id=dispatch_plan['dispatch_id'],
            action='created',
            performed_by='system',
            action_details='Dispatch plan created via Smart Dispatch Planner'
        )
        session.add(dh)
        
        session.commit()
        print(f"✓ Dispatch plan {dispatch_plan['dispatch_id']} saved to database")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error saving to database: {str(e)}")
        return False
        
    finally:
        session.close()


if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    init_database()
    print("✓ Database ready!")
