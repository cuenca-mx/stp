import pytest
from clabe import compute_control_digit
from pydantic.errors import LuhnValidationError, NotDigitError

from stpmex.exc import (
    BankCodeValidationError,
    ClabeControlDigitValidationError,
)
from stpmex.types import Clabe, PaymentCardNumber, validate_digits


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


def test_valid_card_number():
    card_number = '5339220423090005'
    assert (
        PaymentCardNumber.validate_luhn_check_digit(card_number) == card_number
    )


def test_invalid_card_number():
    card_number = '5339220423090006'
    with pytest.raises(LuhnValidationError):
        PaymentCardNumber.validate_luhn_check_digit(card_number)
