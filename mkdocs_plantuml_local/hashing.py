from base64 import urlsafe_b64encode
from hashlib import sha256


def hash_string(to_hash):
    return (
        urlsafe_b64encode(sha256(to_hash.encode("utf-8")).digest())
        .decode("utf-8")
        .rstrip("=")
    )


def hash_list(to_hash):
    return [hash_string(t) for t in to_hash]
