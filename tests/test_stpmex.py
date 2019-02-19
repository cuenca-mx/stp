from clabe import BankCode

from stpmex.helpers import spei_to_stp_bank_code, stp_to_spei_bank_code
import pytest
from stpmex.types import Institucion
from stpmex import Orden


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


def test_create_order_leading_trailing_spaces(orden):
    assert orden.conceptoPago == 'Prueba'
    assert orden.institucionOperante == Institucion.STP.value
    assert orden.cuentaBeneficiario == '072691004495711499'
    assert orden.institucionContraparte == Institucion.BANORTE.value
    assert orden.monto == 1.2
    assert orden.nombreBeneficiario == 'Ricardo Sanchez'


@pytest.mark.vcr
def test_create_orden(orden):
    resp = orden.registra()
    assert resp.descripcionError is None
    assert type(resp.id) is int
    assert resp.id > 0
    assert orden._id == resp.id


@pytest.mark.vcr
def test_empty_monto(orden):
    orden.monto = ''
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_null_monto(orden):
    orden.monto = None
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_is_numeric_monto(orden):
    orden.monto = "dh238d7gd"
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_monto_one(orden):
    orden.monto = WRONG_MONTO_ONE
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_monto_two(orden):
    orden.monto = WRONG_MONTO_TWO
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_empty_concepto(orden):
    orden.conceptoPago = ''
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_null_concepto(orden):
    orden.conceptoPago = None
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_concepto(orden):
    orden.conceptoPago = WRONG_CONCEPTO
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_bad_N_benefit(orden):
    orden.nombreBeneficiario = WRONG_NAME
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_null_N_benefit(orden):
    orden.nombreBeneficiario = None
    with pytest.raises(ValueError):
        orden.registra()


def test_bad_N_ordenante(orden):
    orden.nombreOrdenante = WRONG_NAME
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_emply_clave(orden):
    orden.claveRastreo = ''
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_null_clave(orden):
    orden.claveRastreo = None
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_clave(orden):
    orden.claveRastreo = WRONG_CLAVE
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_wrong_reference(orden):
    orden.referenciaNumerica = WRONG_REFERENCE
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_null_reference(orden):
    orden.referenciaNumerica = None
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_empty_C_beneficiario(orden):
    orden.cuentaBeneficiario = ''
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_null_C_beneficiario(orden):
    orden.cuentaBeneficiario = None
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_beneficiario(orden):
    orden.cuentaBeneficiario = WRONG_ACCOUNT
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_ordenante(orden):
    orden.cuentaOrdenante = WRONG_ACCOUNT
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_folio(orden):
    orden.folioOrigen = WRONG_FOLIO
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_contraparte(orden):
    orden.institucionContraparte = WRONG_INSTITUCION
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_operante(orden):
    orden.institucionOperante = WRONG_INSTITUCION
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_rfcBeneficiario(orden):
    orden.rfcCurpBeneficiario = WRONG_RFC
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_rfcOrdenante(orden):
    orden.rfcCurpOrdenante = WRONG_RFC
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_tipoBeneficiario(orden):
    orden.tipoCuentaBeneficiario = 322
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_tipoOrdenante(orden):
    orden.tipoCuentaOrdenante = 345
    with pytest.raises(ValueError):
        orden.registra()


@pytest.mark.vcr
def test_max_length_tipoPago(orden):
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
