from pydantic import BaseModel, Field


class AadhaarSendOTPRequest(BaseModel):
    aadhaar_number: str = Field(
        ..., min_length=12, max_length=12, json_schema_extra={"example": "123456789012"}
    )


class AadhaarSendOTPResponse(BaseModel):
    status: str = "success"
    transaction_id: str
    message: str = "OTP sent successfully to registered mobile number"


class AadhaarVerifyOTPRequest(BaseModel):
    aadhaar_number: str = Field(
        ..., min_length=12, max_length=12, json_schema_extra={"example": "123456789012"}
    )
    otp: str = Field(
        ..., min_length=6, max_length=6, json_schema_extra={"example": "123456"}
    )


class AadhaarVerifyOTPResponse(BaseModel):
    status: str = "success"
    message: str = "Aadhaar OTP verified successfully"
    verification_status: str = "verified"


class PaymentCreateOrderResponse(BaseModel):
    order_id: str
    amount: int = 50000
    currency: str = "INR"
    status: str = "created"


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str = Field(..., min_length=1)
    razorpay_payment_id: str = Field(..., min_length=1)
    razorpay_signature: str = Field(..., min_length=1)


class PaymentVerifyResponse(BaseModel):
    status: str = "success"
    message: str = "KYC payment verified successfully"
    kyc_payment_status: str = "completed"
