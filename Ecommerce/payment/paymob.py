import requests
from django.conf import settings
import time
from django.shortcuts import redirect
from typing import Dict, Any

class PaymobClient:
    def __init__(self):
        self.api_key = settings.PAYMOB_API_KEY
        self.public_key = settings.PAYMOB_PUBLIC_KEY
        self.secret_key = f"Token {settings.PAYMOB_SECRET_KEY}"
    
    def checkout(self, total_price, integration_id, order_id, user, billing_info=None):
        """Initialize payment with Paymob - returns redirect URL instead of redirecting"""
        if billing_info is None:
            billing_info = {}
            
        # Prepare billing data
        billing_data = {
            "first_name": billing_info.get('first_name') or user.first_name or user.username,
            "last_name": billing_info.get('last_name') or user.last_name or user.username,
            "phone_number": billing_info.get('phone_number'),
            "email": user.email,
            "street": billing_info.get('street'),
            "city": billing_info.get('city', 'NA'),
            "country": "EG",
            "apartment": "NA",
            "floor": "NA",
            "building": "NA",
            "shipping_method": "NA",
            "postal_code": "NA",
            "state": "NA",
        }
        
        payload = {
            "amount": int(total_price * 100),
            "currency": "EGP",
            "payment_methods": [int(integration_id)],
            "billing_data": billing_data,
            "special_reference": f"{order_id}_{int(time.time())}",
            "redirection_url": "http://127.0.0.1:8000/api/payment/callback/",
            "extras": {}
        }

        response = requests.post(
            "https://accept.paymob.com/v1/intention/",
            headers={
                "Content-Type": "application/json",
                "Authorization": self.secret_key,
            },
            json=payload
        )
        data = response.json()

        if 'client_secret' in data:
            # Return the URL instead of redirecting
            return f"https://accept.paymob.com/unifiedcheckout/?publicKey={self.public_key}&clientSecret={data['client_secret']}"
        else:
            raise Exception("Payment initiation failed. Please try again later.")