# Project Overview 

### Run Graph Generator:
```uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload```

### Add Traces:
1. Clone and run all services from this repository:
Jaeger Microservices Simulation (https://github.com/anti-pattern-analyzer/jaeger-microservices-simulation)
2. Run the ```docker-compose``` file to start Jaeger: ```docker-compose up```
3. Run the ```request.py``` file to send requests. Let it run for a few seconds, then exit: ```python request.py```

### View Dependency Graph:
1. Clone and run the frontend application from this repository: Anti-Pattern Analyzer Frontend (https://github.com/anti-pattern-analyzer/anti-pattern-analyzer-fe)
2. Access the web application. The dependency graph will appear on the homepage (/).