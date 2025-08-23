# Global Pooja Booking System

A robust backend system using FastAPI for a platform where users can book Poojas (religious rituals) and optionally add Chadawas (offerings).

## Features

- **User Management**: Registration, authentication, and profile management
- **Pooja Plans**: View and manage different pooja plans
- **Chadawas (Offerings)**: Optional add-ons for poojas
- **Booking System**: Book poojas with date, time, and optional chadawas
- **Payment Integration**: Razorpay integration for secure payments
- **Admin Panel**: Manage poojas, chadawas, view bookings, and track payments

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT / OTP-based login
- **Payments**: Razorpay SDK
- **Email**: SMTP integration for OTP and notifications

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/global-pooja.git
   cd global-pooja
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   # Application
   DEBUG=True
   
   # Database
   DATABASE_URL=postgresql://username:password@localhost:5432/global_pooja
   
   # JWT
   SECRET_KEY=your-secret-key-for-jwt
   
   # Razorpay
   RAZORPAY_KEY_ID=your-razorpay-key-id
   RAZORPAY_KEY_SECRET=your-razorpay-key-secret
   
   # Email
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-email-password
   EMAIL_FROM=noreply@globalpooja.com
   
   # OTP
   OTP_SECRET_KEY=your-otp-secret-key
   ```

5. Initialize the database:
   ```bash
   alembic upgrade head
   ```

## Running the Application

1. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/signup`: Register a new user
- `POST /auth/login`: Login and get access token
- `POST /auth/verify-otp`: Verify OTP for authentication

### User Profile
- `GET /user/profile`: Get current user profile
- `PUT /user/profile`: Update current user profile

### Poojas
- `GET /poojas`: Get list of all poojas
- `GET /poojas/{id}`: Get a specific pooja
- `POST /admin/poojas`: Create a new pooja (Admin only)
- `PUT /admin/poojas/{id}`: Update a pooja (Admin only)
- `DELETE /admin/poojas/{id}`: Delete a pooja (Admin only)

### Chadawas
- `GET /poojas/{id}/chadawas`: Get list of chadawas for a specific pooja
- `POST /admin/chadawas`: Create a new chadawa (Admin only)
- `PUT /admin/chadawas/{id}`: Update a chadawa (Admin only)
- `DELETE /admin/chadawas/{id}`: Delete a chadawa (Admin only)

### Bookings
- `POST /bookings`: Create a new booking
- `GET /bookings/{id}`: Get a specific booking
- `GET /user/bookings`: Get bookings for the current user
- `POST /bookings/{id}/cancel`: Cancel a booking

### Payments
- `POST /payments/create-order`: Create a Razorpay payment order
- `POST /payments/verify`: Verify Razorpay payment signature
- `GET /payments/status/{booking_id}`: Get payment status for a booking

### Admin
- `GET /admin/bookings`: Get list of all bookings (Admin only)
- `GET /admin/payments`: Get list of all payments (Admin only)

## Deployment

### Docker

1. Build the Docker image:
   ```bash
   docker build -t global-pooja .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env global-pooja
   ```

### AWS/DigitalOcean

- Deploy the application on AWS EC2 or DigitalOcean Droplet
- Use RDS or managed PostgreSQL for the database
- Set up a load balancer for high availability
- Configure HTTPS with Let's Encrypt

## License

This project is licensed under the MIT License - see the LICENSE file for details.
