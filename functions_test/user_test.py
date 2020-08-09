import pytest

from functions.shared.users import validate_email

def test_validate_email():
    """Test our simple validator."""
    assert validate_email("abcd") == False
    assert validate_email("abcd@ef.gh") == True
    assert validate_email("ab cd@gmail.com") == False
    assert validate_email("abee[at]gmail.com") == False
    assert validate_email("abee@gmail.party") == True
