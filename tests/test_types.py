import pytest
from clabe import compute_control_digit
from pydantic.errors import NotDigitError

from stpmex.exc import (
    BankCodeValidationError,
    ClabeControlDigitValidationError,
)
from stpmex.types import Clabe, validate_digits


def test_clabe_not_digit():
    with pytest.raises(NotDigitError):
        validate_digits('h' * 18)


def test_invalid_bank_code():
    clabe = '9' * 17
    clabe += compute_control_digit(clabe)
    with pytest.raises(BankCodeValidationError):
        Clabe.validate_bank_code(clabe)


def test_invalid_control_digit():
    clabe = '001' + '9' * 15
    with pytest.raises(ClabeControlDigitValidationError):
        Clabe.validate_control_digit(clabe)
