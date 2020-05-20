import clabe
import pytest
from pydantic import ValidationError

from stpmex.resources import Orden

ORDEN_KWARGS = dict(
    institucionContraparte='40072',
    claveRastreo='CR1564969083',
    monto=1.2,
    tipoPago=1,
    cuentaOrdenante='646180110400000007',
    nombreBeneficiario='Ricardo Sanchez',
    cuentaBeneficiario='072691004495711499',
    conceptoPago='Prueba',
    referenciaNumerica=5273144,
)


def create_orden(**kwargs) -> Orden:
    return Orden(**{**ORDEN_KWARGS, **kwargs})


def test_empty_concepto():
    with pytest.raises(ValidationError) as exc_info:
        create_orden(conceptoPago=' ')
    errors = exc_info.value.errors()
    assert len(errors) == 1
    error = errors[0]
    assert error['loc'] == ('conceptoPago',)
    assert error['type'] == 'value_error.any_str.min_length'


def test_strip_spaces():
    orden = create_orden(conceptoPago=' hello ')
    assert orden.conceptoPago == 'hello'


def test_nonfloat_monto():
    with pytest.raises(ValueError):
        create_orden(monto=5)


def test_truncate_nombre_beneficiario():
    nombre = 'x' * 50
    orden = create_orden(nombreBeneficiario=nombre)
    assert len(orden.nombreBeneficiario) == 39


def test_leading_and_trailing_spaces_nombre_beneficiario():
    nombre = f' {"x" * 38} {"x" * 30} '
    orden = create_orden(nombreOrdenante=nombre)
    assert orden.nombreOrdenante == "x" * 38


def test_invalid_clabe():
    invalid_clabe = '072691004495711490'
    assert not clabe.validate_clabe(invalid_clabe)
    with pytest.raises(ValidationError) as exc_info:
        create_orden(cuentaBeneficiario=invalid_clabe)
    errors = exc_info.value.errors()
    assert len(errors) == 3
    error = errors[0]
    assert error['loc'][0] == 'cuentaBeneficiario'
    assert error['type'] == 'value_error.clabe.control_digit'


def test_wrong_length_cuentaBeneficiario():
    with pytest.raises(ValidationError) as exc_info:
        create_orden(cuentaBeneficiario='1' * 14)
    errors = exc_info.value.errors()
    assert len(errors) == 3
    assert errors[0]['type'] == 'value_error.any_str.min_length'
    assert errors[1]['type'] == 'value_error.any_str.min_length'
    assert errors[2]['type'] == 'value_error.any_str.max_length'
    for error in errors:
        assert error['loc'][0] == 'cuentaBeneficiario'


def test_digits():
    with pytest.raises(ValidationError) as exc_info:
        create_orden(institucionContraparte='9üey0')
    errors = exc_info.value.errors()
    assert len(errors) == 1
    error = errors[0]
    assert error['loc'][0] == 'institucionContraparte'
    assert error['type'] == 'value_error.str.regex'


def test_invalid_bank():
    with pytest.raises(ValidationError) as exc_info:
        create_orden(institucionContraparte='11111')
    errors = exc_info.value.errors()
    assert len(errors) == 1
    error = errors[0]
    assert error['loc'] == ('institucionContraparte',)
    assert error['type'] == 'value_error'


def test_replace_unicode():
    orden = create_orden(
        nombreBeneficiario='Ricardo Sánchez', conceptoPago='está bien, güey 💙'
    )
    assert orden.nombreBeneficiario == 'Ricardo Sanchez'
    assert orden.conceptoPago == 'esta bien, guey'


def test_defaults():
    orden_kwargs = ORDEN_KWARGS.copy()
    orden_kwargs.pop('claveRastreo')
    orden_kwargs.pop('referenciaNumerica')
    orden = Orden(**orden_kwargs)
    assert orden.claveRastreo
    assert orden.referenciaNumerica


def test_zero_referencia_numerica():
    with pytest.raises(ValidationError) as exc_info:
        create_orden(referenciaNumerica='00')
    errors = exc_info.value.errors()
    assert len(errors) == 1
    error = errors[0]
    assert error['loc'] == ('referenciaNumerica',)
    assert error['type'] == 'value_error.number.not_gt'


def test_referencia_numerica_too_high():
    with pytest.raises(ValidationError) as exc_info:
        create_orden(referenciaNumerica=10 ** 7)
    errors = exc_info.value.errors()
    assert len(errors) == 1
    error = errors[0]
    assert error['loc'] == ('referenciaNumerica',)
    assert error['type'] == 'value_error.number.not_lt'


def test_valid_card_number_cuenta_beneficiario():
    orden = create_orden(cuentaBeneficiario='5339220423090005')
    assert orden.claveRastreo
    assert orden.referenciaNumerica


def test_invalid_card_number_cuenta_beneficiario():
    with pytest.raises(ValidationError) as exc_info:
        create_orden(cuentaBeneficiario='5339220423090006')
    errors = exc_info.value.errors()
    assert len(errors) == 3

    error = errors[0]
    assert error['loc'] == ('cuentaBeneficiario',)
    assert error['type'] == 'value_error.any_str.min_length'

    error = errors[1]
    assert error['loc'] == ('cuentaBeneficiario',)
    assert error['type'] == 'value_error.payment_card_number.luhn_check'

    error = errors[2]
    assert error['loc'] == ('cuentaBeneficiario',)
    assert error['type'] == 'value_error.any_str.max_length'
