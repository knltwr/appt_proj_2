# Appointment Booking Application
A RESTful API for service providers to allow patrons to book appointments.

## Key Features
- Create an account.
- Create a profile for your business or service.
- Book appointments with businesses or services that are available on the app.

## Tech Stack
- Language: Python
- Framework: FastAPI (w/ async)
- Database: PostgreSQL (raw SQL, i.e. no ORM) using async connection pool
- Authentication: JWT

## Installation
- Clone repo
- pip install packages from requirements.txt
- Add environment variables (see .env.example)

## Example of app usage
See the swagger documentation for details on routes
1. Create an account: POST /users
2. Login: POST /login
3. Add your service (for which you want to allow users to book appointments): POST /services
4. Add types of appointments for your service (e.g. at a barbershop, one can be 30min for a haircut, while 45min for a haircut and beard trim): POST / services/{service_id}/appt-types
5. Book an appointment w/ a service: POST /appts

## Potential business logic enhancements
- Scheduling exceptions for events like holidays or leaves
- Approve/deny feature for the service owner
- Schedule view to see what slots are available

## Potential tech enhancements
- Employ Docker for portability
- Incorporate NGINX for security and load balancing