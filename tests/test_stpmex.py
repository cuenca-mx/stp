from clabe import BankCode

from stpmex import Orden
from stpmex.helpers import spei_to_stp_bank_code, stp_to_spei_bank_code
from stpmex.types import Institucion
import pytest


WRONG_NAME = "asdfghjklñasdfghjklñasdfghjklñasdfghjklñk"
WRONG_REFERENCE = "12345678"
WRONG_CONCEPTO = "gACeFtxObWskerkNBqzJrWvEvoeofMZmndSuxpKyo"
WRONG_ACCOUNT = "123456789123456789123"
WRONG_CLAVE = "1234567891234567891234567891234"
WRONG_FOLIO = "aHleRDMCqwLQEXfsqFnkdbEbyCZkfqpIAAMrFawVwhnCHVUXAJP"
WRONG_INSTITUCION = 123456
WRONG_MONTO_ONE = 12345678912345678912
WRONG_MONTO_TWO = 234.3443
WRONG_RFC = "GAvmqfKjSvCqvOVIQRJ"


@pytest.mark.vcr
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


@pytest.mark.vcr
def test_create_orden(get_order):
    orden = get_order
    resp = orden.registra()
    assert resp.descripcionError is None
    assert type(resp.id) is int
    assert resp.id > 0
    assert orden._id == resp.id


@pytest.mark.vcr
def test_empty_monto(get_order):
    orden = get_order
    orden.monto = ''
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_null_monto(get_order):
    order = get_order
    order.monto = None
    with pytest.raises(ValueError):
        order.registra()


@pytest.mark.vcr
def test_is_numeric_monto(get_order):
    orden = get_order
    orden.monto = "dh238d7gd"
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_monto_one(get_order):
    orden = get_order
    orden.monto = WRONG_MONTO_ONE
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_monto_two(get_order):
    orden = get_order
    orden.monto = WRONG_MONTO_TWO
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_empty_concepto(get_order):
    orden = get_order
    orden.conceptoPago = ''
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_null_concepto(get_order):
    order = get_order
    order.conceptoPago = None
    with pytest.raises(ValueError):
        order.registra()


@pytest.mark.vcr
def test_max_length_concepto(get_order):
    orden = get_order
    orden.conceptoPago = WRONG_CONCEPTO
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_bad_N_benefit(get_order):
    order = get_order
    order.nombreBeneficiario = WRONG_NAME
    with pytest.raises(ValueError):
        order.registra()


@pytest.mark.vcr
def test_null_N_benefit(get_order):
    order = get_order
    order.nombreBeneficiario = None
    with pytest.raises(ValueError):
        order.registra()


def test_bad_N_ordenante(get_order):
    orden = get_order
    orden.nombreOrdenante = WRONG_NAME
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_emply_clave(get_order):
    order = get_order
    order.claveRastreo = ''
    with pytest.raises(ValueError):
        order.registra()


@pytest.mark.vcr
def test_null_clave(get_order):
    order = get_order
    order.claveRastreo = None
    with pytest.raises(ValueError):
        order.registra()


@pytest.mark.vcr
def test_max_length_clave(get_order):
    order = get_order
    order.claveRastreo = WRONG_CLAVE
    with pytest.raises(ValueError):
        order.registra()


@pytest.mark.vcr
def test_wrong_reference(get_order):
    order = get_order
    order.referenciaNumerica = WRONG_REFERENCE
    with pytest.raises(ValueError):
        order.registra()


@pytest.mark.vcr
def test_null_reference(get_order):
    order = get_order
    order.referenciaNumerica = None
    with pytest.raises(ValueError):
        order.registra()


@pytest.mark.vcr
def test_empty_C_beneficiario(get_order):
    orden = get_order
    orden.cuentaBeneficiario = ''
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_null_C_beneficiario(get_order):
    order = get_order
    order.cuentaBeneficiario = None
    with pytest.raises(ValueError):
        order.registra()


@pytest.mark.vcr
def test_max_length_beneficiario(get_order):
    orden = get_order
    orden.cuentaBeneficiario = WRONG_ACCOUNT
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_ordenante(get_order):
    orden = get_order
    orden.cuentaOrdenante = WRONG_ACCOUNT
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_folio(get_order):
    orden = get_order
    orden.folioOrigen = WRONG_FOLIO
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_contraparte(get_order):
    orden = get_order
    orden.institucionContraparte = WRONG_INSTITUCION
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_operante(get_order):
    orden = get_order
    orden.institucionOperante = WRONG_INSTITUCION
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_rfcBeneficiario(get_order):
    orden = get_order
    orden.rfcCurpBeneficiario = WRONG_RFC
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_rfcOrdenante(get_order):
    orden = get_order
    orden.rfcCurpOrdenante = WRONG_RFC
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_tipoBeneficiario(get_order):
    orden = get_order
    orden.tipoCuentaBeneficiario = 322
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_tipoOrdenante(get_order):
    orden = get_order
    orden.tipoCuentaOrdenante = 345
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_tipoPago(get_order):
    orden = get_order
    orden.tipoPago = 345
    with pytest.raises(ValueError):
        orden.registra()


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
