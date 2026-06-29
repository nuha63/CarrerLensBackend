from fastapi import APIRouter
from pydantic import BaseModel
import requests
import os
import uuid

router = APIRouter(prefix="/payment", tags=["Payment"])

class PaymentRequest(BaseModel):
    amount: float
    customer_name: str
    customer_email: str

@router.post("/init")
def init_payment(data: PaymentRequest):
    # Set up SSLCommerz callback URLs pointing back to the Render backend
    backend_url = "https://carrerlensbackend.onrender.com"
    
    payload = {
        "store_id": os.getenv("SSLC_STORE_ID"),
        "store_passwd": os.getenv("SSLC_STORE_PASSWORD"),
        "total_amount": data.amount,
        "currency": "BDT",
        "tran_id": str(uuid.uuid4()),

        "success_url": f"{backend_url}/payment/success",
        "fail_url": f"{backend_url}/payment/fail",
        "cancel_url": f"{backend_url}/payment/cancel",

        "cus_name": data.customer_name,
        "cus_email": data.customer_email,
        "cus_add1": "Dhaka",
        "cus_city": "Dhaka",
        "cus_country": "Bangladesh",
        "shipping_method": "NO",
        "product_name": "CareerLens Premium",
        "product_category": "Subscription",
        "product_profile": "general",
    }

    res = requests.post(
        "https://sandbox.sslcommerz.com/gwprocess/v4/api.php",
        data=payload
    )

    data_json = res.json()

    return {
        "gateway_url": data_json.get("GatewayPageURL")
    }

@router.post("/success")
def payment_success():
    return {"status": "success"}

@router.post("/fail")
def payment_fail():
    return {"status": "failed"}

@router.post("/cancel")
def payment_cancel():
    return {"status": "cancelled"}
