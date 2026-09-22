from supabase_client import supa
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

class JWTBearer(HTTPBearer):
    def __init__(self):
        super().__init__(auto_error=False)
        
    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(status_code=401, detail={"error": "Access token required"})
        
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=401, detail={"error": "Access token required"})

        if not credentials.credentials:
            raise HTTPException(status_code=401, detail={"error": "Access token required"})

        print(credentials)


def sign_up(email: str, password: str):
    res = supa.auth.sign_up({"email": email, "password": password})

    return res.user

def sign_in(email: str, password: str) -> str:
    res = supa.auth.sign_in_with_password({"email": email, "password": password})

    return res.session.access_token