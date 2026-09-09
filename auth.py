from supabase_client import supa


def sign_up(email: str, password: str) -> str:
    res = supa.auth.sign_up({"email": email, "password": password})

    return res.session.access_token

def sign_in(email: str, password: str) -> str:
    res = supa.auth.sign_in_with_password({"email": email, "password": password})

    return res.session.access_token