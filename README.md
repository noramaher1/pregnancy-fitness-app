<<<<<<< HEAD
#Pregnancy Fitness APP
![Welcome page](docs/welcome.png)
![Tracker page](docs/tracker.png)
Three Python (FastAPI) microservices and MongoDB, deployable with Docker Compose or Kubernetes.

Component	Role
web-gateway	Serves the UI, aggregates the two backends, the only service exposed outside the cluster
workout-service	Stores workouts in MongoDB, the only service that touches the database
recommendation-service	Trimester rules plus the last 7 days of load from workout-service
workout-db	MongoDB on a persistent volume
Full step-by-step instructions, diagrams and the video and report outline are in GUIDE.md.

Quick start:

cp .env.example .env
docker compose up --build
Kubernetes: see section 8 of the guide. Manifests are in `k8s/`.

Scaling note: this is a small app. To make scaling meaningful, assume thousands of users log workouts daily and recommendation logic is CPU-heavy. `SIMULATE_CPU_MS` stands in for that work.
=======
# pregnancy-fitness-app
Microservice-based Pregnancy Fitness Application using FastAPI, MongoDB, Docker and Kubernetes.
>>>>>>> 51624ac0d85cdbf609631c5fe6ed22a9bbac07a6
