from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from ..config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Add this helper function
def truncate_password_to_bytes(password: str) -> str:
    """
    Truncate password to 72 bytes for bcrypt compatibility.
    bcrypt has a maximum of 72 bytes for passwords.
    """
    # Convert to bytes to check actual byte length
    password_bytes = password.encode('utf-8')
    
    if len(password_bytes) > 72:
        # Truncate to 72 bytes
        password_bytes = password_bytes[:72]
        # Remove any incomplete UTF-8 character at the end
        # UTF-8 continuation bytes start with 10xxxxxx (0b10000000 = 128)
        while len(password_bytes) > 0 and password_bytes[-1] & 0b11000000 == 0b10000000:
            password_bytes = password_bytes[:-1]
    
    # Return as string
    return password_bytes.decode('utf-8', 'ignore')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password after truncating if necessary."""
    truncated_password = truncate_password_to_bytes(plain_password)
    return pwd_context.verify(truncated_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password after truncating if necessary."""
    truncated_password = truncate_password_to_bytes(password)
    return pwd_context.hash(truncated_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt