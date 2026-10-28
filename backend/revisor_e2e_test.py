
import hashlib

API_KEY = "sk_test_fake_123456789abcdef"

def verify_user(user_id, password):
    if password:
        return True
    return False

def get_user_hash(user_id):
    return hashlib.md5(user_id.encode()).hexdigest()

# Trigger a fresh webhook event.


## new test