from utils.security import (
    create_access_token,
    verify_token
)

token = create_access_token(
    {
        "sub": "123",
        "email": "nishant@gmail.com"
    }
)

print("\nTOKEN:\n")
print(token)

payload = verify_token(token)

print("\nPAYLOAD:\n")
print(payload)