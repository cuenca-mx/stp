from clabe import BankCode

from stpmex import Orden
from stpmex.helpers import spei_to_stp_bank_code, stp_to_spei_bank_code
from stpmex.types import Institucion
import pytest
import vcr


WRONG_BENEFIT = "asdfghjklñasdfghjklñasdfghjklñasdfghjklñ"
WRONG_REFERENCE = "12345678"


@vcr.use_cassette(cassette_library_dir='tests/cassettes')
def test_join_fields(initialize_stpmex):
    orden = Orden(
        institucionContraparte='846',
        fechaOperacion='20160810',
        folioOrigen='1q2w33e',
        claveRastreo='1q2w33e',
        monto='121.00',
        tipoPago='1',
        tipoCuentaOrdenante='40',
        tipoCuentaBeneficiario='40',
        nombreBeneficiario='eduardo',
        cuentaBeneficiario='846180000300000004',
        rfcCurpBeneficiario='ND',
        emailBeneficiario='fernanda.cedillo@stpmex.com',
        conceptoPago='pago prueba',
        referenciaNumerica='123123',
        topologia='T',
        medioEntrega='3',
        prioridad='0'
    )
    joined = ('||846|TAMIZI|20160810|1q2w33e|1q2w33e||121.00|1|40||||40|'
              'eduardo|846180000300000004|ND|fernanda.cedillo@stpmex.com|||||'
              'pago prueba||||||123123||T||3|0|||').encode('utf-8')

    assert orden._joined_fields == joined


@pytest.fixture
def get_order():
    return Orden(
        conceptoPago='Prueba',
        institucionOperante=Institucion.STP.value,
        cuentaBeneficiario='072691004495711499',
        institucionContraparte=Institucion.BANORTE.value,
        monto=1.2,
        nombreBeneficiario='Ricardo Sanchez')


def test_create_order_leading_trailing_spaces(initialize_stpmex):
    order = Orden(
        conceptoPago='    Prueba    ',
        institucionOperante=Institucion.STP.value,
        cuentaBeneficiario='    072691004495711499    ',
        institucionContraparte=Institucion.BANORTE.value,
        monto=1.2,
        nombreBeneficiario='    Ricardo Sanchez    '
    )
    assert order.conceptoPago == 'Prueba'
    assert order.institucionOperante == Institucion.STP.value
    assert order.cuentaBeneficiario == '072691004495711499'
    assert order.institucionContraparte == Institucion.BANORTE.value
    assert order.monto == 1.2
    assert order.nombreBeneficiario == 'Ricardo Sanchez'


@vcr.use_cassette(cassette_library_dir='tests/cassettes')
def test_create_orden(initialize_stpmex, get_order):
    orden = get_order
    resp = orden.registra()
    assert resp.descripcionError is None
    assert type(resp.id) is int
    assert resp.id > 0
    assert orden._id == resp.id


@vcr.use_cassette(cassette_library_dir='tests/cassettes')
def test_empty_concepto(initialize_stpmex, get_order):
    orden = get_order
    orden.conceptoPago = ''
    with pytest.raises(ValueError):
        orden.registra()


@vcr.use_cassette(cassette_library_dir='tests/cassettes')
def test_bad_benefit(initialize_stpmex, get_order):
    order = get_order
    order.nombreBeneficiario = WRONG_BENEFIT
    with pytest.raises(ValueError):
        order.registra()


@vcr.use_cassette(cassette_library_dir='tests/cassettes')
def test_null_benefit(initialize_stpmex, get_order):
    order = get_order
    order.nombreBeneficiario = None
    with pytest.raises(ValueError):
        order.registra()


@vcr.use_cassette(cassette_library_dir='tests/cassettes')
def test_null_clave(initialize_stpmex, get_order):
    order = get_order
    order.claveRastreo = None
    with pytest.raises(ValueError):
        order.registra()


@vcr.use_cassette(cassette_library_dir='tests/cassettes')
def test_null_concepto(initialize_stpmex, get_order):
    order = get_order
    order.conceptoPago = None
    with pytest.raises(ValueError):
        order.registra()


@vcr.use_cassette(cassette_library_dir='tests/cassettes')
def test_wrong_reference(initialize_stpmex, get_order):
    order = get_order
    order.referenciaNumerica = WRONG_REFERENCE
    with pytest.raises(ValueError):
        order.registra()


@vcr.use_cassette(cassette_library_dir='tests/cassettes')
def test_null_reference(initialize_stpmex, get_order):
    order = get_order
    order.referenciaNumerica = None
    with pytest.raises(ValueError):
        order.registra()


def test_invalid_spei_bank():
    spei_bank = '001'
    stp_code = spei_to_stp_bank_code(spei_bank)
    assert stp_code is None


def test_valid_spei_bank():
    spei_bank = '002'
    stp_code = spei_to_stp_bank_code(spei_bank)
    assert stp_code == Institucion.BANAMEX


def test_invalid_stp_bank():
    stp_bank = 9999999
    spei_code = stp_to_spei_bank_code(stp_bank)
    assert spei_code is None


def test_valid_stp_bank():
    stp_bank = 40002
    spei_code = stp_to_spei_bank_code(stp_bank)
    assert spei_code == BankCode.BANAMEX.value


def test_max_length(initialize_stpmex, get_order):
    order = get_order
    order.claveRastreo = '1234567891234567891234567891234'
    with pytest.raises(ValueError):
        order.registra()
