# Deployment Guide

## Local Development

### Prerequisites
- Python 3.9+
- pip

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install package in development mode:
```bash
pip install -e .
```

3. Run the examples:
```bash
python examples/basic_usage.py
python examples/exotic_options.py
```

### Running the Web Application

1. Start the FastAPI server:
```bash
cd api
python main.py
```

Or using uvicorn directly:
```bash
uvicorn api.main:app --reload
```

2. Open your browser to:
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Docker Deployment

### Build and run with Docker

```bash
# Build the image
docker build -t mc-options-pricer .

# Run the container
docker run -p 8000:8000 mc-options-pricer
```

### Using Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Cloud Deployment

### Heroku

1. Install Heroku CLI
2. Create a new app:
```bash
heroku create your-app-name
```

3. Add a `Procfile`:
```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

4. Deploy:
```bash
git push heroku main
```

### Railway

1. Connect your GitHub repository to Railway
2. Railway will auto-detect the Python app
3. Set environment variables if needed
4. Deploy!

### AWS EC2

1. Launch an EC2 instance (Ubuntu)
2. SSH into the instance
3. Install Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

4. Clone your repository and run:
```bash
git clone <your-repo>
cd mc-options-pricer
docker-compose up -d
```

5. Configure security group to allow port 8000

### DigitalOcean

Similar to AWS EC2, or use their App Platform for easier deployment.

## Performance Tuning

For production deployment:

1. Use Gunicorn with multiple workers:
```bash
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. Configure worker count based on CPU cores:
```python
workers = (2 * cpu_count()) + 1
```

3. Add caching for frequently requested calculations

4. Consider using Redis for session management

## Monitoring

Add monitoring with:
- Prometheus for metrics
- Grafana for visualization
- Sentry for error tracking

## Security

For production:
1. Add rate limiting
2. Implement authentication
3. Use HTTPS
4. Validate all inputs
5. Set CORS properly

## Testing

Run tests before deployment:
```bash
pytest
pytest --cov=src/mc_pricer
```
