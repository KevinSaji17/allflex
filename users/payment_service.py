"""
Payment Gateway Integration
---------------------------
Handles credit purchases via Razorpay payment gateway.
"""
import os
import json
from decimal import Decimal
from typing import Dict, Optional

# Payment gateway settings (configure in .env)
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')
PAYMENT_CURRENCY = 'INR'
PAYMENT_GATEWAY_ENABLED = bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET)


def is_payment_gateway_enabled() -> bool:
    """Check if payment gateway is configured and enabled."""
    return PAYMENT_GATEWAY_ENABLED


def create_payment_order(amount: Decimal, currency: str = PAYMENT_CURRENCY, notes: Dict = None) -> Optional[Dict]:
    """
    Create a payment order with Razorpay.
    
    Args:
        amount: Amount in INR
        currency: Currency code (default: INR)
        notes: Additional metadata
    
    Returns:
        Order details dict or None if gateway not configured
    """
    if not PAYMENT_GATEWAY_ENABLED:
        return {
            'error': 'Payment gateway not configured',
            'demo_mode': True,
            'message': 'Using demo credits. Configure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env for real payments.'
        }
    
    try:
        import razorpay
        
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        
        # Amount should be in paise (smallest currency unit)
        amount_paise = int(float(amount) * 100)
        
        order_data = {
            'amount': amount_paise,
            'currency': currency,
            'payment_capture': 1  # Auto capture payment
        }
        
        if notes:
            order_data['notes'] = notes
        
        order = client.order.create(data=order_data)
        
        return {
            'success': True,
            'order_id': order['id'],
            'amount': amount,
            'currency': currency,
            'key_id': RAZORPAY_KEY_ID
        }
    
    except ImportError:
        return {
            'error': 'Razorpay library not installed',
            'demo_mode': True,
            'message': 'Install razorpay: pip install razorpay'
        }
    except Exception as e:
        print(f"[ERROR] create_payment_order: {e}")
        return {
            'error': str(e),
            'demo_mode': True
        }


def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """
    Verify Razorpay payment signature for security.
    
    Args:
        order_id: Razorpay order ID
        payment_id: Razorpay payment ID
        signature: Payment signature
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not PAYMENT_GATEWAY_ENABLED:
        return False
    
    try:
        import razorpay
        import hmac
        import hashlib
        
        # Generate signature
        message = f"{order_id}|{payment_id}"
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return generated_signature == signature
    
    except Exception as e:
        print(f"[ERROR] verify_payment_signature: {e}")
        return False


def process_payment_callback(payment_data: Dict) -> Dict:
    """
    Process payment callback from Razorpay.
    
    Args:
        payment_data: Payment callback data
    
    Returns:
        Processing result
    """
    order_id = payment_data.get('razorpay_order_id')
    payment_id = payment_data.get('razorpay_payment_id')
    signature = payment_data.get('razorpay_signature')
    
    if not all([order_id, payment_id, signature]):
        return {
            'success': False,
            'error': 'Missing required payment data'
        }
    
    # Verify signature
    is_valid = verify_payment_signature(order_id, payment_id, signature)
    
    if not is_valid:
        return {
            'success': False,
            'error': 'Invalid payment signature'
        }
    
    return {
        'success': True,
        'order_id': order_id,
        'payment_id': payment_id,
        'message': 'Payment verified successfully'
    }


def get_payment_status(payment_id: str) -> Optional[Dict]:
    """
    Get payment status from Razorpay.
    
    Args:
        payment_id: Razorpay payment ID
    
    Returns:
        Payment status dict or None
    """
    if not PAYMENT_GATEWAY_ENABLED:
        return None
    
    try:
        import razorpay
        
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        payment = client.payment.fetch(payment_id)
        
        return {
            'status': payment['status'],
            'amount': payment['amount'] / 100,  # Convert from paise to rupees
            'currency': payment['currency'],
            'method': payment.get('method'),
            'email': payment.get('email'),
            'contact': payment.get('contact')
        }
    
    except Exception as e:
        print(f"[ERROR] get_payment_status: {e}")
        return None
