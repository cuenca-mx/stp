import re
import unicodedata
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Type

from cuenca_validations.validators import validate_digits
from pydantic import ConstrainedStr, StrictStr
from pydantic.validators import (
    constr_length_validator,
    constr_strip_whitespace,
    str_validator,
)

if TYPE_CHECKING:
    from pydantic.typing import CallableGenerator  # pragma: no cover


def unicode_to_ascii(unicode: str) -> str:
    v = unicodedata.normalize('NFKD', unicode).encode('ascii', 'ignore')
    return v.decode('ascii')


class AsciiStr(ConstrainedStr):
    @classmethod
    def validate(cls, value: str) -> str:
        value = super().validate(value)
        return unicode_to_ascii(value).strip()


class StpStr(AsciiStr):
    """
    based on:
    https://stpmex.zendesk.com/hc/es/articles/360038242071-Registro-de-Cuentas-de-Personas-f%C3%ADsicas
    """

    @classmethod
    def validate(cls, value: str) -> str:
        value = super().validate(value)
        value = re.sub(r'[-,.]', ' ', value)
        value = value.upper()
        return value


def truncated_str(length: int) -> Type[str]:
    namespace = dict(
        strip_whitespace=True, min_length=1, curtail_length=length
    )
    return type('TruncatedStrValue', (AsciiStr,), namespace)


def truncated_stp_str(length: int) -> Type[str]:
    namespace = dict(
        strip_whitespace=True, min_length=1, curtail_length=length
    )
    return type('TruncatedStpStrValue', (StpStr,), namespace)


class Estado(str, Enum):
    """
    Based on: https://stpmex.zendesk.com/hc/es/articles/360040200791
    """

    capturada = 'C'
    pendiente_liberar = 'PL'
    liberada = 'L'
    pendiente_autorizar = 'PA'
    autorizada = 'A'
    enviada = 'E'
    liquidada = 'LQ'
    cancelada = 'CN'
    traspaso_liberado = 'TL'
    traspaso_capturado = 'TC'
    traspaso_autorizado = 'TA'
    traspaso_liquidado = 'TLQ'
    traspaso_cancelado = 'TCL'
    recibida = 'R'
    por_devolver = 'XD'
    devuelta = 'D'
    por_enviar_confirmacion = 'CXO'
    confirmacion_enviada = 'CCE'
    confirmada = 'CCO'
    confirmacion_rechazada = 'CCR'
    por_cancelar = 'XC'
    cancelada_local = 'CL'
    cancelada_rechazada = 'CR'
    rechazada_local = 'RL'
    cancelada_adapter = 'CA'
    rechazada_adapter = 'RA'
    enviada_adapter = 'EA'
    rechazada_banxico = 'RB'
    eliminada = 'EL'
    por_retornar = 'XR'
    retornada = 'RE'
    exportacion_poa = 'EP'
    exportacion_cep = 'EC'


class Prioridad(int, Enum):
    normal = 0
    alta = 1


class TipoCuenta(int, Enum):
    card = 3
    phone_number = 10
    clabe = 40


class Genero(str, Enum):
    mujer = 'M'
    hombre = 'H'


class Curp(StrictStr):
    min_length = 18
    max_length = 18
    regex = re.compile(r'^[A-Z]{4}[0-9]{6}[A-Z]{6}[A-Z|0-9][0-9]$')


class Rfc(StrictStr):
    min_length = 12
    max_length = 13


class EntidadFederativa(int, Enum):
    # NE = Nacido en el Extranjero. Aún STP no soporte
    AS = 1  # Aguascalientes
    BC = 2  # Baja California
    BS = 3  # Baja California Sur
    CC = 4  # Campeche
    CS = 5  # Chiapas
    CH = 6  # Chihuahua
    CL = 7  # Coahuila
    CM = 8  # Colima
    DF = 9  # CDMX
    DG = 10  # Durango
    MC = 11  # Estado de México
    GT = 12  # Guanajuato
    GR = 13  # Guerrero
    HG = 14  # Hidalgo
    JC = 15  # Jalisco
    MN = 16  # Michoacan
    MS = 17  # Morelos
    NT = 18  # Nayarit
    NL = 19  # Nuevo León
    OC = 20  # Oaxaca
    PL = 21  # Puebla
    QT = 22  # Querétaro
    QR = 23  # Quintana Roo
    SP = 24  # San Luis Potosí
    SL = 25  # Sinaloa
    SR = 26  # Sonora
    TC = 27  # Tabasco
    TS = 28  # Tamualipas
    TL = 29  # Tlaxcala
    VZ = 30  # Veracruz
    YN = 31  # Yucatán
    ZS = 32  # Zacatecas


class Pais(int, Enum):
    """
    Based on https://stpmex.zendesk.com/hc/es/articles/360037876272
    """

    SE_DESCONOCE = 0
    AF = 1  # Republica Islamica de Afganistan
    AL = 2  # Republica de Albania
    DE = 3  # Republica Federal de Alemania
    HV = 4  # Alto Volta
    AD = 5  # Principado de Andorra
    AO = 6  # Republica de Angola
    AI = 7  # Anguila
    AG = 8  # Antigua y Barbuda
    AN = 9  # Antillas Neerlandesas
    SA = 10  # Reino de Arabia Saudita
    SJ = 11  # Svalbard y Jan Mayen
    DZ = 12  # Republica Democratica Popular de Argelia
    AR = 13  # Republica Argentina
    AM = 14  # Republica de Armenia
    AW = 15  # Aruba
    AC = 16  # Islas de Ascencion
    AU = 17  # Commonwealth de Australia
    AT = 18  # Republica de Austria
    AZ = 19  # Republica de Azerbaiyan
    BS = 20  # Commonwealth de Las Bahamas
    BH = 21  # Reino de Bahrein
    BD = 22  # Republica Popular de Bangladesh
    BB = 23  # Barbados
    BY = 24  # Republica de Belarus
    BE = 25  # Reino de Belgica
    BZ = 26  # Belice
    BM = 27  # Bermudas
    MM = 28  # Birmania
    BO = 29  # Republica de Bolivia
    BA = 30  # Bosnia Herzegovina
    BW = 31  # Republica de Botswana
    BR = 32  # Republica Federal de Brasil
    BN = 33  # Brunei Malasia
    BG = 34  # Republica de Bulgaria
    BI = 35  # Republica de Burundi
    BT = 36  # Reino de Butan
    CM = 37  # Republica de Camerun
    CA = 39  # Dominio de Canada
    CO = 40  # Republica de Colombia
    KR = 43  # Republica de Corea
    CI = 44  # Republica de Costa de Marfil
    CR = 45  # Republica de Costa Rica
    HR = 46  # Republica de Croacia
    CU = 47  # Republica de Cuba
    CW = 48  # Curazao
    TD = 49  # Republica de Chad
    CZ = 50  # Republica Checa
    CL = 51  # Republica de Chile
    CN = 52  # Republica Popular China
    DK = 54  # Reino de Dinamarca
    EC = 56  # Republica del Ecuador
    EG = 57  # Republica Arabe de Egipto
    SV = 58  # Republica de El Salvador
    AE = 59  # Emiratos Arabes Unidos
    ES = 60  # Reino de Espana
    KW = 61  # Estado de Kuwait
    QA = 62  # Estado de Qatar
    US = 63  # Estados Unidos de Norteamerica
    EE = 64  # Republica de Estonia
    ET = 65  # Republica Democratica Federal de Etiopia
    PH = 66  # Republica de Las Filipinas
    FI = 67  # Republica de Finlandia
    FR = 68  # Republica de Francia
    GA = 69  # Republica de Gabon
    GM = 70  # Republica de La Gambia
    GE = 71  # Georgia
    GH = 72  # Republica de Ghana
    GI = 73  # Gibraltar
    GD = 74  # Granada
    GR = 75  # Grecia
    GL = 76  # Groenlandia
    GU = 77  # Guam
    GT = 78  # Guatemala
    GF = 79  # Guayana Francesa
    GN = 80  # Guinea
    GQ = 81  # Guinea Ecuatorial
    GY = 83  # Guyana
    HT = 86  # Republica de Haiti
    NL = 87  # Holanda
    HN = 88  # Republica de Honduras
    HK = 89  # Hong Kong
    HU = 90  # Hungria
    IN = 91  # Republica de India
    ID = 92  # Republica de Indonesia
    GB = 93  # Reino Unido
    IQ = 94  # Republica de Irak
    IR = 95  # Republica Islamica de Iran
    IE = 96  # Republica de Irlanda
    KY = 97  # Islas Caiman
    NF = 98  # Isla de Norfolk
    PM = 100  # Isla de San Pedro y Miquelin
    IM = 101  # Isla de Man
    IS = 103  # Islandia
    IC = 105  # Islas Canarias
    CK = 106  # Islas Cook
    CC = 107  # Islas de Cocos O Kelling
    GG = 108  # Guernesey
    FK = 109  # Islas Malvinas
    MH = 110  # Republica de Las Islas Marshall
    SB = 112  # Islas Salomon
    TC = 113  # Islas Turcas y Caicos
    VG = 114  # Islas Virgenes Britanicas
    IL = 116  # Estado de Israel
    IT = 117  # Republica de Italia
    JM = 118  # Jamaica
    JP = 119  # Japon
    JO = 120  # Reino Hashemita de Jordania
    KZ = 121  # Republica de Kazajstan
    KE = 122  # Republica de Kenya
    KG = 123  # Republica de Kirguistan
    KI = 124  # Republica de Kiribati
    LA = 127  # Republica Democratica Popular de Laos
    LS = 129  # Reino de Lesotho
    LB = 130  # Republica del Libano
    LR = 131  # Republica de Liberia
    LI = 133  # Principado de Liechenstein
    LT = 134  # Republica de Lituania
    LU = 135  # Gran Ducado de Luxemburgo
    MO = 136  # Region Especialadminiostrativademacaodelarepublicapopularchina
    YU = 137  # Antigua Republica Yugoslava de Macedonia
    MG = 138  # Republica de Madagascar
    MY = 140  # Malasia
    MW = 141  # Republica de Malawi
    ML = 142  # Republica de Mali
    MT = 143  # Republica de Malta
    MA = 144  # Reino de Marruecos
    MU = 145  # Republica de Mauricio
    MR = 146  # Republica Islamica de Mauritania
    MC = 148  # Principado de Monaco
    MN = 149  # Mongolia
    MS = 150  # Montserrat
    MZ = 151  # Republica de Mozambique
    NA = 152  # Republica de Namibia
    NR = 153  # Republica de Nauru
    NP = 154  # Estado de Nepal
    NI = 156  # Republica de Nicaragua
    NE = 268  # Niger
    NG = 158  # Republica Federal de Nigeria
    NU = 159  # Niue
    NO = 161  # Reino de Noruega
    NZ = 162  # Nueva Zelanda
    OM = 163  # Sultanato de Oman
    PW = 164  # Republica de Palaos
    PA = 165  # Republica Panama
    PK = 166  # Republica Islamica de Paquistan
    PY = 167  # Republica de Paraguay
    PE = 168  # Republica del Peru
    PN = 169  # Islas Pitcairn
    PF = 170  # Polinesia Francesa
    PL = 171  # Republica de Polonia
    PT = 172  # Republica de Portugal
    PR = 173  # Estado Libre Asociado de Puerto Rico
    TO = 175  # Reino de Tonga
    CV = 177  # Republica de Cabo Verde
    CY = 178  # Republica de Chipre
    MV = 181  # Republica de Las Maldivas
    SC = 182  # Republica de Seychelles
    TN = 183  # Republica de Tunez
    VU = 184  # Republica de Vanuatu
    YE = 185  # Republica del Yemen
    DO = 186  # Republica Dominicana
    MX = 187  # Mexico
    UY = 188  # Republica Oriental de Uruguay
    RW = 190  # Republica de Ruanda
    RO = 191  # Rumania
    RU = 192  # Federacion Rusa, Rusia
    AS = 194  # Samoa Americana
    VC = 197  # San Vicente y Las Granadinas
    SN = 199  # Republica de Senegal
    SL = 201  # Republica de Sierra Leona
    SK = 203  # Slovakia
    SI = 204  # Slovenia
    SO = 205  # Somalia
    LK = 206  # Republica Democratica Socialista de Sri Lanka
    ZA = 207  # Republica de Sudafrica
    SD = 208  # Republica del Sudan
    SE = 209  # Reino de Suecia
    CH = 210  # Confederacion Helvetica, Suiza
    SR = 211  # Republica de Surinam
    TH = 212  # Reino de Tailandia
    TW = 213  # Republica de China, Taiwan
    TZ = 214  # Republica Unida de Tanzania
    TJ = 215  # Republica de Tajikistan
    TG = 216  # Republica de Togo
    TK = 217  # Tokelau
    TT = 219  # Republica de Trinidad y Tobago
    SH = 220  # Tristan de Cunha
    TM = 222  # Turkmenistan
    TR = 223  # Republica de Turquia
    TV = 224  # Tuvalu
    UA = 225  # Ucrania
    UG = 226  # Uganda
    UZ = 227  # Republica de Uzbekistan
    VE = 228  # Republica Bolivariana de Venezuela
    VN = 229  # Republica Socialista de Vietnam
    ZR = 231  # Republica de Zaire
    ZM = 232  # Republica de Zambia
    KN = 235  # San Cristobal y Nieves
    SG = 236  # Republica de Singapure
    WS = 237  # Samoa
    BF = 238  # Burkina Faso
    CX = 240  # Isla de Christmas
    KM = 241  # Comoras
    ER = 242  # Eritrea
    FO = 243  # Islas Faroe
    FJ = 244  # Fiyi
    MQ = 245  # Martinica
    FM = 246  # Micronesia
    MD = 247  # Moldova
    ME = 248  # Montenegro
    NC = 249  # Nueva Caledonia
    PS = 250  # Palestina
    PG = 251  # Papua Nueva Guinea
    SZ = 252  # Suazilandia
    ST = 253  # Santo Tome y Principe
    RS = 254  # Serbia
    ZW = 255  # Zimbabue
    AQ = 256  # Antartida
    CD = 259  # Republica Democratica del Congo
    AX = 257  # Islas Åland
    BV = 258  # Isla Bouvet
    CP = 260  # Clipperton
    GP = 261  # Guadalupe
    GS = 262  # Georgia del Sur E Islas Sandwich del Sur
    HM = 263  # Islas Heard y Mcdonald
    IO = 264  # Territorio Britanico del Oceano Indico
    JE = 265  # Jersey
    LV = 266  # Letonia
    MP = 267  # Islas Marianas del Norte
    RE = 270  # Reunion
    TF = 271  # Territorios Australes Franceses
    UM = 272  # Islas Menores Alejadas de Los Estados Unidos
    VA = 273  # Santa Sede Estado de La Ciudad del Vaticano
    WF = 274  # Wallis y Futuna
    YT = 275  # Mayotte


class TipoOperacion(str, Enum):
    enviada = 'E'
    recibida = 'R'


class MxPhoneNumber(str):
    strip_whitespace: ClassVar[bool] = True
    min_length: ClassVar[int] = 10
    max_length: ClassVar[int] = 10

    @classmethod
    def __get_validators__(cls) -> 'CallableGenerator':
        yield str_validator
        yield constr_strip_whitespace
        yield constr_length_validator
        yield validate_digits
