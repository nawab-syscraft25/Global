import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.server = settings.SMTP_SERVER
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM

    def send_email(self, to_email: str, subject: str, message: str, is_html: bool = False) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            message: Email message content
            is_html: Whether the message is HTML
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach message body
            if is_html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_otp_email(self, to_email: str, otp: str) -> bool:
        """
        Send OTP email
        
        Args:
            to_email: Recipient email address
            otp: One-time password
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Your OTP for Global Pooja Booking"
        
        # Create HTML message
        html_message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ padding: 20px; }}
                .otp {{ font-size: 24px; font-weight: bold; color: #4a6ee0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <p>Dear User,</p>
                <p>Your OTP for Global Pooja Booking is: <span class="otp">{otp}</span></p>
                <p>This OTP is valid for 5 minutes.</p>
                <p>If you didn't request this OTP, please ignore this email.</p>
                <p>Regards,<br>Global Pooja Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_message, is_html=True)
    
    def send_booking_confirmation(self, to_email: str, booking_details: dict) -> bool:
        """
        Send booking confirmation email
        
        Args:
            to_email: Recipient email address
            booking_details: Booking details
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Pooja Booking Confirmation"
        
        pooja_name = booking_details.get('pooja_name', '')
        booking_date = booking_details.get('booking_date', '')
        booking_id = booking_details.get('booking_id', '')
        total_amount = booking_details.get('total_amount', 0)
        
        # Create HTML message
        html_message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ padding: 20px; }}
                .heading {{ color: #4a6ee0; }}
                .details {{ margin: 20px 0; }}
                .details div {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2 class="heading">Booking Confirmation</h2>
                <p>Dear User,</p>
                <p>Your pooja booking has been confirmed. Here are the details:</p>
                
                <div class="details">
                    <div><span class="label">Booking ID:</span> {booking_id}</div>
                    <div><span class="label">Pooja:</span> {pooja_name}</div>
                    <div><span class="label">Date & Time:</span> {booking_date}</div>
                    <div><span class="label">Total Amount:</span> ₹{total_amount}</div>
                </div>
                
                <p>Thank you for using our service.</p>
                <p>Regards,<br>Global Pooja Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_message, is_html=True)
    
    def send_payment_confirmation(self, to_email: str, payment_details: dict) -> bool:
        """
        Send payment confirmation email
        
        Args:
            to_email: Recipient email address
            payment_details: Dictionary containing payment details
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Payment Confirmation - Global Pooja"
        
        # Extract payment details
        payment_id = payment_details.get('payment_id', '')
        order_id = payment_details.get('order_id', '')
        amount = payment_details.get('amount', 0)
        currency = payment_details.get('currency', 'INR')
        date = payment_details.get('date', '')
        puja_name = payment_details.get('puja_name', '')
        
        # Create HTML message
        html_message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ padding: 20px; }}
                .heading {{ color: #4a6ee0; }}
                .details {{ margin: 20px 0; background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .details div {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
                .highlight {{ color: #4a6ee0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2 class="heading">Payment Confirmation</h2>
                <p>Dear User,</p>
                <p>We've received your payment. Thank you!</p>
                
                <div class="details">
                    <div><span class="label">Payment ID:</span> {payment_id}</div>
                    <div><span class="label">Order ID:</span> {order_id}</div>
                    <div><span class="label">Amount:</span> {currency} {amount}</div>
                    <div><span class="label">Date:</span> {date}</div>
                    <div><span class="label">For:</span> {puja_name} Pooja</div>
                </div>
                
                <p>If you have any questions about your booking or payment, please contact our support team.</p>
                <p>Regards,<br>Global Pooja Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_message, is_html=True)
