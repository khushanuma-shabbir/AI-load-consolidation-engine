# 🚀 Deployment Guide
## AI Load Consolidation & Logistics Intelligence Platform

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Configuration](#configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB, Recommended 16GB
- **Storage**: 10GB free space
- **CPU**: Multi-core processor recommended

### Software Requirements
- **Python**: 3.11 or higher
- **pip**: Latest version
- **PostgreSQL**: 15+ (optional for production)
- **Docker**: 20.10+ (optional for containerized deployment)
- **Docker Compose**: 2.0+ (optional)

---

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd AI_LOAD_CONSOLIDATION_PROBLEM
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### Step 5: Process Data

```bash
# Option A: Quick demo (generates sample results)
python quick_demo.py

# Option B: Full pipeline (processes actual data)
python data_processing/pipeline.py
```

### Step 6: Start Services

**Terminal 1 - API Backend:**
```bash
python backend/main.py
```
Access API at: http://localhost:8000  
API Docs: http://localhost:8000/docs

**Terminal 2 - Dashboard:**
```bash
streamlit run dashboard/app.py
```
Access Dashboard at: http://localhost:8501

---

## Docker Deployment

### Step 1: Build Images

```bash
docker-compose build
```

### Step 2: Start All Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- FastAPI backend (port 8000)
- Streamlit dashboard (port 8501)

### Step 3: Verify Services

```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs dashboard
```

### Step 4: Access Applications

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **PostgreSQL**: localhost:5432

### Step 5: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Production Deployment

### Cloud Platform Options

#### Option 1: AWS Deployment

**Architecture:**
- **EC2**: FastAPI backend
- **RDS**: PostgreSQL database
- **S3**: Data storage
- **CloudFront**: Dashboard CDN
- **ELB**: Load balancing

**Steps:**

1. **Launch EC2 Instance**
```bash
# t3.large recommended (2 vCPU, 8GB RAM)
# Ubuntu 22.04 LTS
```

2. **Install Dependencies**
```bash
sudo apt update
sudo apt install python3.11 python3-pip postgresql-client
pip3 install -r requirements.txt
```

3. **Set Up RDS PostgreSQL**
```bash
# Create RDS instance
# Note endpoint for DATABASE_URL
```

4. **Configure Environment**
```bash
export DATABASE_URL="postgresql://user:pass@rds-endpoint:5432/logistics"
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

5. **Start Services with Systemd**

Create `/etc/systemd/system/logistics-api.service`:
```ini
[Unit]
Description=Logistics API Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/AI_LOAD_CONSOLIDATION_PROBLEM
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/usr/bin/python3 backend/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable logistics-api
sudo systemctl start logistics-api
```

#### Option 2: Azure Deployment

**Architecture:**
- **App Service**: FastAPI backend
- **Container Instances**: Docker deployment
- **Azure Database for PostgreSQL**: Database
- **Blob Storage**: Data storage

**Steps:**

1. **Create App Service**
```bash
az webapp create --resource-group logistics-rg \
  --plan logistics-plan --name logistics-api \
  --runtime "PYTHON:3.11"
```

2. **Deploy Code**
```bash
az webapp deployment source config-zip \
  --resource-group logistics-rg \
  --name logistics-api \
  --src deploy.zip
```

#### Option 3: Google Cloud Platform

**Architecture:**
- **Cloud Run**: Containerized backend
- **Cloud SQL**: PostgreSQL database
- **Cloud Storage**: Data storage

**Steps:**

1. **Build and Push Container**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/logistics-api
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy logistics-api \
  --image gcr.io/PROJECT_ID/logistics-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: logistics-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: logistics-api
  template:
    metadata:
      labels:
        app: logistics-api
    spec:
      containers:
      - name: api
        image: logistics-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

Apply:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

## Configuration

### Environment Variables

**Required:**
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/logistics
API_HOST=0.0.0.0
API_PORT=8000
```

**Optional:**
```env
# AI/ML
GROK_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Optimization Parameters
DEFAULT_TRUCK_CAPACITY=45000
FUEL_PRICE_PER_GALLON=3.50
COST_PER_TRUCK_PER_DAY=500

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

### Database Configuration

**PostgreSQL Setup:**
```sql
CREATE DATABASE logistics;
CREATE USER admin WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE logistics TO admin;
```

### Nginx Reverse Proxy

**Configuration:**
```nginx
server {
    listen 80;
    server_name api.logistics.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name dashboard.logistics.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Monitoring & Maintenance

### Health Checks

**API Health Check:**
```bash
curl http://localhost:8000/
```

**Database Health Check:**
```bash
pg_isready -h localhost -p 5432
```

### Logging

**Application Logs:**
```bash
# View API logs
tail -f logs/api.log

# View dashboard logs
tail -f logs/dashboard.log
```

**Docker Logs:**
```bash
docker-compose logs -f --tail=100
```

### Backup Strategy

**Database Backup:**
```bash
# Daily backup
pg_dump -U admin logistics > backup_$(date +%Y%m%d).sql

# Automated backup script
0 2 * * * /usr/bin/pg_dump -U admin logistics > /backup/logistics_$(date +\%Y\%m\%d).sql
```

**Data Backup:**
```bash
# Backup processed data
tar -czf processed_data_backup.tar.gz processed_data/
tar -czf optimization_results_backup.tar.gz optimization/results/
```

### Performance Monitoring

**Metrics to Track:**
- API response time
- Database query performance
- Memory usage
- CPU utilization
- Disk I/O

**Tools:**
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **New Relic**: APM monitoring
- **DataDog**: Infrastructure monitoring

---

## Troubleshooting

### Common Issues

#### Issue 1: Module Not Found Error

**Error:**
```
ModuleNotFoundError: No module named 'sklearn'
```

**Solution:**
```bash
pip install scikit-learn
# or
pip install -r requirements.txt
```

#### Issue 2: Database Connection Failed

**Error:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Verify connection string in .env
```

#### Issue 3: Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

#### Issue 4: Out of Memory

**Error:**
```
MemoryError: Unable to allocate array
```

**Solution:**
```python
# Process data in chunks
chunksize = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunksize):
    process_chunk(chunk)
```

#### Issue 5: Slow Performance

**Symptoms:**
- API requests taking > 5 seconds
- Dashboard loading slowly

**Solutions:**
1. **Enable Caching:**
```python
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)
```

2. **Optimize Database Queries:**
```sql
CREATE INDEX idx_trip_id ON trips(trip_id);
CREATE INDEX idx_load_id ON loads(load_id);
```

3. **Use Connection Pooling:**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20
)
```

### Debug Mode

**Enable Debug Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**FastAPI Debug Mode:**
```python
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="debug")
```

### Getting Help

1. **Check Documentation**: README.md, PROJECT_SUMMARY.md
2. **Review Logs**: Check application and system logs
3. **API Documentation**: http://localhost:8000/docs
4. **GitHub Issues**: Report bugs and request features
5. **Email Support**: support@logistics-ai.com

---

## Security Best Practices

### Production Checklist

- [ ] Change default passwords
- [ ] Use HTTPS/TLS certificates
- [ ] Enable firewall rules
- [ ] Set up authentication (OAuth2/JWT)
- [ ] Implement rate limiting
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Database encryption at rest
- [ ] Secure environment variables
- [ ] API key rotation policy

### SSL/TLS Setup

**Using Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.logistics.com
```

### Authentication

**Implement JWT:**
```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    # Verify token
    return {"message": "Authenticated"}
```

---

## Scaling Guidelines

### Horizontal Scaling

**Load Balancer Configuration:**
```
Client → Load Balancer → [API Instance 1]
                      → [API Instance 2]
                      → [API Instance 3]
```

### Vertical Scaling

**Resource Recommendations:**

| Users | CPU | RAM | Storage |
|-------|-----|-----|---------|
| 1-10 | 2 cores | 8GB | 50GB |
| 10-50 | 4 cores | 16GB | 100GB |
| 50-100 | 8 cores | 32GB | 200GB |
| 100+ | 16+ cores | 64GB+ | 500GB+ |

### Database Scaling

**Read Replicas:**
```python
# Master for writes
write_engine = create_engine(MASTER_DB_URL)

# Replica for reads
read_engine = create_engine(REPLICA_DB_URL)
```

---

## Maintenance Schedule

### Daily
- Monitor system health
- Check error logs
- Verify backups

### Weekly
- Review performance metrics
- Update datasets
- Clean temporary files

### Monthly
- Security updates
- Database optimization
- Cost analysis

### Quarterly
- Feature updates
- Model retraining
- Architecture review

---

## Rollback Procedure

**In case of failed deployment:**

1. **Stop New Services:**
```bash
docker-compose down
```

2. **Restore Previous Version:**
```bash
git checkout <previous-commit>
docker-compose up -d
```

3. **Restore Database:**
```bash
psql -U admin logistics < backup_latest.sql
```

4. **Verify System:**
```bash
curl http://localhost:8000/status
```

---

## Contact & Support

- **Documentation**: README.md, PROJECT_SUMMARY.md
- **API Docs**: http://localhost:8000/docs
- **GitHub**: <repository-url>
- **Email**: support@logistics-ai.com

---

**Deployment Status**: ✅ **PRODUCTION READY**

*Last Updated: June 3, 2026*
