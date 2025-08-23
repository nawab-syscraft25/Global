-- Supabase schema for Global Pooja application
-- Based on ideal database schema structure

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set up auth schema (if not already created by Supabase)
CREATE SCHEMA IF NOT EXISTS auth;

-- ==============================
-- Users & Authentication
-- ==============================
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    mobile VARCHAR(15) UNIQUE NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('super_admin', 'admin', 'user')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.otp_logins (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES public.users(id) ON DELETE CASCADE,
    otp_code VARCHAR(6) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================
-- Pujas & Images
-- ==============================
CREATE TABLE IF NOT EXISTS public.pujas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.puja_images (
    id SERIAL PRIMARY KEY,
    puja_id INT REFERENCES public.pujas(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL
);

-- ==============================
-- Global Plans & Mappings
-- ==============================
CREATE TABLE IF NOT EXISTS public.plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url TEXT,
    actual_price NUMERIC(10,2) NOT NULL,
    discounted_price NUMERIC(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.puja_plans (
    id SERIAL PRIMARY KEY,
    puja_id INT REFERENCES public.pujas(id) ON DELETE CASCADE,
    plan_id INT REFERENCES public.plans(id) ON DELETE CASCADE,
    UNIQUE(puja_id, plan_id)
);

-- ==============================
-- Global Chadawas & Mappings
-- ==============================
CREATE TABLE IF NOT EXISTS public.chadawas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url TEXT,
    price NUMERIC(10,2) NOT NULL,
    requires_note BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS public.puja_chadawas (
    id SERIAL PRIMARY KEY,
    puja_id INT REFERENCES public.pujas(id) ON DELETE CASCADE,
    chadawa_id INT REFERENCES public.chadawas(id) ON DELETE CASCADE,
    UNIQUE(puja_id, chadawa_id)
);

-- ==============================
-- Bookings
-- ==============================
CREATE TABLE IF NOT EXISTS public.bookings (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES public.users(id) ON DELETE CASCADE,
    puja_id INT REFERENCES public.pujas(id),
    plan_id INT REFERENCES public.plans(id),
    booking_date TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
    puja_link TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.booking_chadawas (
    id SERIAL PRIMARY KEY,
    booking_id INT REFERENCES public.bookings(id) ON DELETE CASCADE,
    chadawa_id INT REFERENCES public.chadawas(id),
    note TEXT
);

-- ==============================
-- Payments (Razorpay Integration)
-- ==============================
CREATE TABLE IF NOT EXISTS public.payments (
    id SERIAL PRIMARY KEY,
    booking_id INT REFERENCES public.bookings(id) ON DELETE CASCADE,
    razorpay_order_id VARCHAR(100) NOT NULL,
    razorpay_payment_id VARCHAR(100),
    razorpay_signature VARCHAR(255),
    amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    status VARCHAR(20) DEFAULT 'created' CHECK (status IN ('created', 'pending', 'success', 'failed', 'refunded')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_id ON public.users(id);
CREATE INDEX IF NOT EXISTS idx_poojas_id ON public.poojas(id);
CREATE INDEX IF NOT EXISTS idx_chadawas_id ON public.chadawas(id);
CREATE INDEX IF NOT EXISTS idx_bookings_id ON public.bookings(id);
CREATE INDEX IF NOT EXISTS idx_booking_chadawa_id ON public.booking_chadawa(id);
CREATE INDEX IF NOT EXISTS idx_payments_id ON public.payments(id);

-- Booking Chadawas table
CREATE TABLE IF NOT EXISTS public.booking_chadawas (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES public.bookings(id) ON DELETE CASCADE,
    chadawa_id INTEGER REFERENCES public.chadawas(id),
    note TEXT
);

-- Payments table
CREATE TABLE IF NOT EXISTS public.payments (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES public.bookings(id) ON DELETE CASCADE,
    razorpay_order_id VARCHAR(100) NOT NULL,
    razorpay_payment_id VARCHAR(100),
    razorpay_signature VARCHAR(255),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    status payment_status DEFAULT 'created' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create indexes
-- ==============================
-- Indexes for Performance
-- ==============================
CREATE INDEX IF NOT EXISTS idx_users_id ON public.users(id);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_mobile ON public.users(mobile);
CREATE INDEX IF NOT EXISTS idx_otp_logins_user_id ON public.otp_logins(user_id);
CREATE INDEX IF NOT EXISTS idx_pujas_id ON public.pujas(id);
CREATE INDEX IF NOT EXISTS idx_puja_images_puja_id ON public.puja_images(puja_id);
CREATE INDEX IF NOT EXISTS idx_plans_id ON public.plans(id);
CREATE INDEX IF NOT EXISTS idx_puja_plans_puja_id ON public.puja_plans(puja_id);
CREATE INDEX IF NOT EXISTS idx_puja_plans_plan_id ON public.puja_plans(plan_id);
CREATE INDEX IF NOT EXISTS idx_chadawas_id ON public.chadawas(id);
CREATE INDEX IF NOT EXISTS idx_puja_chadawas_puja_id ON public.puja_chadawas(puja_id);
CREATE INDEX IF NOT EXISTS idx_puja_chadawas_chadawa_id ON public.puja_chadawas(chadawa_id);
CREATE INDEX IF NOT EXISTS idx_bookings_id ON public.bookings(id);
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON public.bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_booking_chadawas_booking_id ON public.booking_chadawas(booking_id);
CREATE INDEX IF NOT EXISTS idx_payments_id ON public.payments(id);
CREATE INDEX IF NOT EXISTS idx_payments_booking_id ON public.payments(booking_id);
CREATE INDEX IF NOT EXISTS idx_payments_razorpay_order_id ON public.payments(razorpay_order_id);

-- ==============================
-- Row Level Security (RLS) Policies
-- ==============================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.otp_logins ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pujas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.puja_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.puja_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chadawas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.puja_chadawas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.booking_chadawas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

-- Policies for users table
CREATE POLICY "Users can view their own data" ON public.users
    FOR SELECT USING (auth.uid()::text = id::text);
    
CREATE POLICY "Admins can view all users" ON public.users
    FOR SELECT USING (auth.jwt() ->> 'role' IN ('admin', 'super_admin'));

CREATE POLICY "Admins can insert users" ON public.users
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' IN ('admin', 'super_admin'));

CREATE POLICY "Users can update their own data" ON public.users
    FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Admins can update any user" ON public.users
    FOR UPDATE USING (auth.jwt() ->> 'role' IN ('admin', 'super_admin'));

-- Policies for bookings table
CREATE POLICY "Users can view their own bookings" ON public.bookings
    FOR SELECT USING (auth.uid()::text = user_id::text);
    
CREATE POLICY "Admins can view all bookings" ON public.bookings
    FOR SELECT USING (auth.jwt() ->> 'role' IN ('admin', 'super_admin'));

CREATE POLICY "Users can create their own bookings" ON public.bookings
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
    
CREATE POLICY "Admins can update any booking" ON public.bookings
    FOR UPDATE USING (auth.jwt() ->> 'role' IN ('admin', 'super_admin'));

-- Policies for payments table
CREATE POLICY "Users can view their own payments" ON public.payments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.bookings b
            WHERE b.id = booking_id AND auth.uid()::text = b.user_id::text
        )
    );
    
CREATE POLICY "Admins can view all payments" ON public.payments
    FOR SELECT USING (auth.jwt() ->> 'role' IN ('admin', 'super_admin'));

CREATE POLICY "Payment creation based on booking ownership" ON public.payments
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.bookings b
            WHERE b.id = booking_id AND auth.uid()::text = b.user_id::text
        )
    );

CREATE POLICY "Admins can update any payment" ON public.payments
    FOR UPDATE USING (auth.jwt() ->> 'role' IN ('admin', 'super_admin'));

-- ==============================
-- Functions and Triggers
-- ==============================

-- Function for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at timestamp
CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON public.users
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER set_timestamp_pujas
BEFORE UPDATE ON public.pujas
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER set_timestamp_payments
BEFORE UPDATE ON public.payments
FOR EACH ROW EXECUTE FUNCTION update_timestamp();
