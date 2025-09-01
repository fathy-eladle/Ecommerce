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
    
    def checkout(self, total_price, integration_id, order_id):
        """Initialize payment with Paymob"""
        payload = {
            "amount": int(total_price * 100),
            "currency": "EGP",
            "payment_methods": [int(integration_id)],
            "billing_data": {
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "+201066415951",
                "email": "test@example.com",
            },
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
        print("DEBUG Paymob response:", data)  # For debugging

        if 'client_secret' in data:
            return redirect(f"https://accept.paymob.com/unifiedcheckout/?publicKey={self.public_key}&clientSecret={data['client_secret']}")
        else:
            raise Exception("Payment initiation failed. Please try again later.")
