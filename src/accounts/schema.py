from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from .serializers import *


activation_code_view_schema = extend_schema(
    summary="Activate User Account",
    description="Activate a user account using an activation code within 10 minutes of registration. "
                "This endpoint also enforces a rate limit to prevent abuse; exceeding the allowed number of "
                "requests results in a 429 (Too Many Requests) response.",
    request=ActivationCodeSerializer,
    responses={
        200: OpenApiResponse(
            response=MessageSerializer,
            description="User activated successfully.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={"detail": "User activated successfully."},
                    response_only=True
                )
            ],
        ),
        400: OpenApiResponse(
            response=MessageSerializer,
            description="Activation failed due to an invalid activation code, an expired code, or the user is already activated.",
            examples=[
                OpenApiExample(
                    name="Already Activated",
                    value={"detail": "User is already activated."},
                    response_only=True
                ),
                OpenApiExample(
                    name="Expired Code",
                    value={"detail": "Activation code has expired."},
                    response_only=True
                ),
                OpenApiExample(
                    name="Invalid Code",
                    value={"detail": "Invalid activation code."},
                    response_only=True
                )
            ],
        ),
        429: OpenApiResponse(
            response=MessageSerializer,
            description="Too many requests: The rate limit for activation attempts has been exceeded.",
            examples=[
                OpenApiExample(
                    name="Rate Limit Exceeded",
                    value={"detail": "Too many requests"},
                    response_only=True
                )
            ],
        ),
    },
    examples=[
        OpenApiExample(
            name="Valid Activation Code",
            value={"activation_code": "12345678"},
            description="A valid activation code that can be used to activate the account.",
            request_only=True,
        ),
        OpenApiExample(
            name="Invalid Activation Code",
            value={"detail": "Invalid activation code."},
            description="This response occurs when the activation code is invalid or does not exist.",
            response_only=True,
        ),
    ]
)


password_reset_request_description = """
Initiates the password reset process by sending a reset link to the provided email address.

If the email address is associated with an existing user account, an email containing a secure password reset link will be sent.
This link allows the user to reset their password securely.

**Note**: To prevent email enumeration attacks, this endpoint will **always return a success message**, even if the email does not belong to any user.

### 🔹 Expected Flow:
1. User submits their email address.
2. If valid, a reset link is generated containing a unique token and encoded user ID.
3. The reset link is sent to the user's email address.
4. User can follow the link to set a new password.

### 🔹 Security Considerations:
- **No user enumeration risk** → Response is **always `200 OK`**, even if the email is invalid.
- **Time-limited reset links** → Tokens expire after a predefined period.
- **Rate-limited requests** → Too many reset requests result in **`429 Too Many Requests`**.
- **Tokens are cryptographically secure** → Prevents unauthorized access.
"""

password_reset_request_schema = extend_schema(
    summary="Request Password Reset",
    description=password_reset_request_description,
    request=PasswordResetRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=MessageSerializer,
            description="Password reset link has been sent if the email exists.",
            examples=[
                OpenApiExample(
                    name="Reset Link Sent (Success or Non-existent Email)",
                    value={"detail": "If this email exists, a reset link has been sent."},
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            description="Invalid request format.",
            examples=[
                OpenApiExample(
                    name="Invalid Email Format",
                    value={"email": ["Enter a valid email address."]},
                    response_only=True,
                ),
            ],
        ),
        429: OpenApiResponse(
            description="Too many requests (Throttling applied).",
            examples=[
                OpenApiExample(
                    name="Too Many Requests",
                    value={"detail": "Request was throttled. Try again later."},
                    response_only=True,
                ),
            ],
        ),
    }
)


password_reset_confirm_description = """
Completes the password reset process by validating the provided **UID**, **reset token**, 
and **new password** fields.

This endpoint is used after the user clicks on the password reset link sent to their email. 
The link contains a unique **token** and **encoded user ID (UID)** which must be submitted along with 
the new password.

### 🔑 Expected Flow:
1. User clicks on the reset password link received via email.
2. The frontend collects and submits:
   - `uid`: Encoded user ID from the link.
   - `token`: Password reset token from the link.
   - `password`: New password to set.
   - `retyped_password`: Confirmation of the new password.
3. Backend verifies the token and UID, checks password match, and resets the user's password.

### 🔒 Security Considerations:
- The **token** and **UID** ensure that only the rightful account owner can reset the password.
- Password validation uses Django's built-in validators to enforce strong passwords.
- **Throttle classes** are applied to this endpoint (with a rate of 10/hour by default) to mitigate 
  brute-force attempts against the password reset confirmation process.

### ⚙️ Notes:
- Both `password` and `retyped_password` must be identical.
- The `token` is **time-limited** and becomes invalid after use or expiration.
- On success, a confirmation message is returned. On failure, error details are provided.
"""

password_reset_confirm_schema = extend_schema(
    summary="Confirm Password Reset",
    description=password_reset_confirm_description,
    request=PasswordResetConfirmSerializer,
    responses={
        200: OpenApiResponse(
            response=MessageSerializer,
            description="Password reset successfully.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={"detail": "Password has been reset successfully."},
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=None,
            description="Invalid token, expired link, mismatched passwords, or missing fields.",
            examples=[
                OpenApiExample(
                    name="Invalid Token",
                    value={"token": "Token is expired or invalid."},
                    response_only=True,
                ),
                OpenApiExample(
                    name="Password Mismatch",
                    value={"retyped_password": "Passwords do not match."},
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid UID",
                    value={"uid": "Invalid or malformed UID."},
                    response_only=True,
                ),
                OpenApiExample(
                    name="Password Validation Error",
                    value={"password": ["This password is too short. It must contain at least 8 characters."]},
                    response_only=True,
                ),
            ],
        ),
        429: OpenApiResponse(
            description="Too many requests have been made, and the rate limit has been exceeded. Please try again later.",
            examples=[
                OpenApiExample(
                    name="Throttled",
                    value={"detail": "Too many requests"},
                    response_only=True,
                ),
            ],
        ),
    },
)

