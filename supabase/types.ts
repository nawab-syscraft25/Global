export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: number
          name: string
          email: string | null
          mobile: string
          role: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          name: string
          email?: string | null
          mobile: string
          role?: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          name?: string
          email?: string | null
          mobile?: string
          role?: string
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      otp_logins: {
        Row: {
          id: number
          user_id: number
          otp_code: string
          is_verified: boolean
          expires_at: string
          created_at: string
        }
        Insert: {
          id?: number
          user_id: number
          otp_code: string
          is_verified?: boolean
          expires_at: string
          created_at?: string
        }
        Update: {
          id?: number
          user_id?: number
          otp_code?: string
          is_verified?: boolean
          expires_at?: string
          created_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "otp_logins_user_id_fkey"
            columns: ["user_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      pujas: {
        Row: {
          id: number
          name: string
          description: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          name: string
          description?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          name?: string
          description?: string | null
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      puja_images: {
        Row: {
          id: number
          puja_id: number
          image_url: string
        }
        Insert: {
          id?: number
          puja_id: number
          image_url: string
        }
        Update: {
          id?: number
          puja_id?: number
          image_url?: string
        }
        Relationships: [
          {
            foreignKeyName: "puja_images_puja_id_fkey"
            columns: ["puja_id"]
            referencedRelation: "pujas"
            referencedColumns: ["id"]
          }
        ]
      }
      plans: {
        Row: {
          id: number
          name: string
          description: string | null
          image_url: string | null
          actual_price: number
          discounted_price: number | null
          created_at: string
        }
        Insert: {
          id?: number
          name: string
          description?: string | null
          image_url?: string | null
          actual_price: number
          discounted_price?: number | null
          created_at?: string
        }
        Update: {
          id?: number
          name?: string
          description?: string | null
          image_url?: string | null
          actual_price?: number
          discounted_price?: number | null
          created_at?: string
        }
        Relationships: []
      }
      puja_plans: {
        Row: {
          id: number
          puja_id: number
          plan_id: number
        }
        Insert: {
          id?: number
          puja_id: number
          plan_id: number
        }
        Update: {
          id?: number
          puja_id?: number
          plan_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "puja_plans_puja_id_fkey"
            columns: ["puja_id"]
            referencedRelation: "pujas"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "puja_plans_plan_id_fkey"
            columns: ["plan_id"]
            referencedRelation: "plans"
            referencedColumns: ["id"]
          }
        ]
      }
      chadawas: {
        Row: {
          id: number
          name: string
          description: string | null
          image_url: string | null
          price: number
          requires_note: boolean
        }
        Insert: {
          id?: number
          name: string
          description?: string | null
          image_url?: string | null
          price: number
          requires_note?: boolean
        }
        Update: {
          id?: number
          name?: string
          description?: string | null
          image_url?: string | null
          price?: number
          requires_note?: boolean
        }
        Relationships: []
      }
      puja_chadawas: {
        Row: {
          id: number
          puja_id: number
          chadawa_id: number
        }
        Insert: {
          id?: number
          puja_id: number
          chadawa_id: number
        }
        Update: {
          id?: number
          puja_id?: number
          chadawa_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "puja_chadawas_puja_id_fkey"
            columns: ["puja_id"]
            referencedRelation: "pujas"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "puja_chadawas_chadawa_id_fkey"
            columns: ["chadawa_id"]
            referencedRelation: "chadawas"
            referencedColumns: ["id"]
          }
        ]
      }
      bookings: {
        Row: {
          id: number
          user_id: number
          puja_id: number | null
          plan_id: number | null
          booking_date: string
          status: string
          puja_link: string | null
          created_at: string
        }
        Insert: {
          id?: number
          user_id: number
          puja_id?: number | null
          plan_id?: number | null
          booking_date?: string
          status?: string
          puja_link?: string | null
          created_at?: string
        }
        Update: {
          id?: number
          user_id?: number
          puja_id?: number | null
          plan_id?: number | null
          booking_date?: string
          status?: string
          puja_link?: string | null
          created_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "bookings_user_id_fkey"
            columns: ["user_id"]
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "bookings_puja_id_fkey"
            columns: ["puja_id"]
            referencedRelation: "pujas"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "bookings_plan_id_fkey"
            columns: ["plan_id"]
            referencedRelation: "plans"
            referencedColumns: ["id"]
          }
        ]
      }
      booking_chadawas: {
        Row: {
          id: number
          booking_id: number
          chadawa_id: number | null
          note: string | null
        }
        Insert: {
          id?: number
          booking_id: number
          chadawa_id?: number | null
          note?: string | null
        }
        Update: {
          id?: number
          booking_id?: number
          chadawa_id?: number | null
          note?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "booking_chadawas_booking_id_fkey"
            columns: ["booking_id"]
            referencedRelation: "bookings"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "booking_chadawas_chadawa_id_fkey"
            columns: ["chadawa_id"]
            referencedRelation: "chadawas"
            referencedColumns: ["id"]
          }
        ]
      }
      payments: {
        Row: {
          id: number
          booking_id: number
          razorpay_order_id: string
          razorpay_payment_id: string | null
          razorpay_signature: string | null
          amount: number
          currency: string
          status: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          booking_id: number
          razorpay_order_id: string
          razorpay_payment_id?: string | null
          razorpay_signature?: string | null
          amount: number
          currency?: string
          status?: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          booking_id?: number
          razorpay_order_id?: string
          razorpay_payment_id?: string | null
          razorpay_signature?: string | null
          amount?: number
          currency?: string
          status?: string
          created_at?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "payments_booking_id_fkey"
            columns: ["booking_id"]
            referencedRelation: "bookings"
            referencedColumns: ["id"]
          }
        ]
      }
    }
    Views: {}
    Functions: {}
    Enums: {
      user_role: 'super_admin' | 'admin' | 'user'
      booking_status: 'pending' | 'confirmed' | 'completed' | 'cancelled'
      payment_status: 'created' | 'pending' | 'success' | 'failed' | 'refunded'
    }
  }
}

export type Tables<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Row']
export type Enums<T extends keyof Database['public']['Enums']> = Database['public']['Enums'][T]
