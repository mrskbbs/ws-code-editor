from hashlib import sha256

def sha256salt(payload: str, salt: str) -> str:
    return sha256(str(payload + salt).encode()).hexdigest()
