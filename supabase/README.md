# Supabase Integration for Global Pooja FastAPI Application

This directory contains the configuration and schema files required to use Supabase as the database backend for the Global Pooja FastAPI application.

## Files

- `schema.sql`: Contains the SQL schema definition for the Supabase database, including tables, indexes, constraints, and RLS policies.
- `client.py`: Python configuration file for the Supabase client.
- `services/payment_service.py`: Python service class for payment operations using Supabase.

## Setup Instructions

### 1. Create a Supabase Project

1. Go to [Supabase](https://supabase.com/) and sign up or log in.
2. Create a new project and note your project URL and anon key.

### 2. Configure Environment Variables

Add the following environment variables to your `.env` file:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Initialize the Database Schema

1. Navigate to the SQL Editor in your Supabase dashboard.
2. Copy and paste the contents of `schema.sql` into the editor.
3. Run the SQL script to create all tables, indexes, and policies.

### 4. Install Required Dependencies

Add to your `requirements.txt`:

```
supabase==1.0.4
```

Then install:

```bash
pip install supabase
```

### 5. Update Application Configuration

You can now use Supabase alongside or instead of your current PostgreSQL + SQLAlchemy setup:

```python
from supabase.client import get_supabase
from supabase.services.payment_service import SupabasePaymentService

# Initialize service
payment_service = SupabasePaymentService()

# Example: Create a payment
payment_data = {
    'booking_id': 1,
    'razorpay_order_id': 'order_abc123',
    'amount': 100.00,
    'currency': 'INR',
    'status': 'created'
}
payment = await payment_service.create_payment(payment_data)
```

## Schema Structure

Your ideal schema includes the following organized sections:

### Users & Authentication
- `users`: User profiles with roles
- `otp_logins`: OTP verification system

### Pujas & Images
- `pujas`: Puja definitions
- `puja_images`: Images for pujas

### Global Plans & Mappings
- `plans`: Available plans with pricing
- `puja_plans`: Many-to-many mapping between pujas and plans

### Global Chadawas & Mappings
- `chadawas`: Available offerings with pricing
- `puja_chadawas`: Many-to-many mapping between pujas and chadawas

### Bookings
- `bookings`: User booking records
- `booking_chadawas`: Selected chadawas for each booking

### Payments (Razorpay Integration)
- `payments`: Payment records with Razorpay integration

## Row Level Security (RLS)

The schema includes comprehensive RLS policies that ensure:

1. Users can only access their own data
2. Admins can access all data
3. Proper authorization checks for all operations
4. Data modification is restricted based on ownership and roles

## Migration Strategy

To migrate from SQLAlchemy to Supabase:

1. **Parallel Implementation**: Keep existing SQLAlchemy code while implementing Supabase services
2. **Gradual Migration**: Start with read operations, then move to write operations
3. **Feature Testing**: Test each feature thoroughly with Supabase before switching
4. **Authentication Update**: Consider using Supabase Auth for user management
