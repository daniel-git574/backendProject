from pydantic import BaseModel

class TokenResponse(BaseModel):
    # The JWT string the server returns after successful login.
    access_token: str
    # Token type is typically 'bearer' for OAuth2 flows.
    token_type: str