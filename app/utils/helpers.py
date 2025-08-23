import logging
from typing import Dict, Any
import uuid

logger = logging.getLogger(__name__)

def generate_unique_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def calculate_total_amount(base_price: float, additional_prices: list = None) -> float:
    """
    Calculate total amount from base price and additional prices
    
    Args:
        base_price: Base price
        additional_prices: List of additional prices
        
    Returns:
        Total amount
    """
    total = base_price
    
    if additional_prices:
        total += sum(additional_prices)
    
    return total

def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format currency amount
    
    Args:
        amount: Amount
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == "INR":
        return f"₹{amount:.2f}"
    
    return f"{currency} {amount:.2f}"

def log_error(message: str, error: Exception = None) -> None:
    """
    Log error message
    
    Args:
        message: Error message
        error: Exception object
    """
    if error:
        logger.error(f"{message}: {str(error)}")
    else:
        logger.error(message)
