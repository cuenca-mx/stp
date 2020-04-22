import pytest
from pydantic.errors import LuhnValidationError

from stpmex.types import PaymentCardNumber


def test_valid_card_number():
    card_number = '5339220423090005'
    assert (
        PaymentCardNumber.validate_luhn_check_digit(card_number) == card_number
    )


def test_invalid_card_number():
    card_number = '5339220423090006'
    with pytest.raises(LuhnValidationError):
        PaymentCardNumber.validate_luhn_check_digit(card_number)
