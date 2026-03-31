from hashlib import sha256


def hash_in_sha256(string: str) -> str:
    """
    Encrypt the given string using SHA-256.
    
    Parameters
    ----------
    string : str
        The input string to be hashed.

    Returns
    -------
    str        The SHA-256 hash of the input string.

    Examples
    --------
    >>> hash_in_sha256("hello world")
    'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
    """
    return sha256(string.encode()).hexdigest()
