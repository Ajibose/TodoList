from supabase_client import supa
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from supabase_auth.errors import AuthApiError

class JWTBearer(HTTPBearer):
    def __init__(self):
        super().__init__(auto_error=False)
        
    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(status_code=401, detail={"error": "Access token required"})
            
            if not credentials.credentials:
                raise HTTPException(status_code=401, detail={"error": "Access token required"})

            user = self.verify_jwt(credentials.credentials)

            if not user:
                raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})

            return {"id": user.id, "email": user.email, "created_at": user.created_at}

        else:
            raise HTTPException(status_code=401, detail={"error": "Access token required"})


    def verify_jwt(self, token: str) -> dict | None:
        try:
            response = supa.auth.get_user(jwt=token)
            if response and response.user:
                return response.user

            return None
        except Exception:
            return None



def sign_up(email: str, password: str):
    res = supa.auth.sign_up({"email": email, "password": password})

    return res.user

def sign_in(email: str, password: str) -> dict | None:
    try:
        res = supa.auth.sign_in_with_password({"email": email, "password": password})
        return {"access_token": res.session.access_token, "refresh_token": res.session.refresh_token}
    except AuthApiError:
        return None

def sign_out():
    supa.auth.sign_out()