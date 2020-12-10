import re
import unicodedata
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, Optional, Type

from clabe.types import validate_digits
from pydantic import ConstrainedStr, StrictStr, constr
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


def digits(
    min_length: Optional[int] = None, max_length: Optional[int] = None
) -> Type[str]:
    return constr(regex=r'^\d+$', min_length=min_length, max_length=max_length)


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
    AF = 1  #  REPUBLICA ISLAMICA DE AFGANISTAN
    AL = 2  #  REPUBLICA DE ALBANIA
    DE = 3  #  REPUBLICA FEDERAL DE ALEMANIA
    HV = 4  #  ALTO VOLTA
    AD = 5  #  PRINCIPADO DE ANDORRA
    AO = 6  #  REPUBLICA DE ANGOLA
    AI = 7  #  ANGUILA
    AG = 8  #  ANTIGUA Y BARBUDA
    AN = 9  #  ANTILLAS NEERLANDESAS
    SA = 10  #  REINO DE ARABIA SAUDITA
    SJ = 11  #  SVALBARD Y JAN MAYEN
    DZ = 12  #  REPUBLICA DEMOCRATICA POPULAR DE ARGELIA
    AR = 13  #  REPUBLICA ARGENTINA
    AM = 14  #  REPUBLICA DE ARMENIA
    AW = 15  #  ARUBA
    AC = 16  #  ISLAS DE ASCENCION
    AU = 17  #  COMMONWEALTH DE AUSTRALIA
    AT = 18  #  REPUBLICA DE AUSTRIA
    AZ = 19  #  REPUBLICA DE AZERBAIYAN
    BS = 20  #  COMMONWEALTH DE LAS BAHAMAS
    BH = 21  #  REINO DE BAHREIN
    BD = 22  #  REPUBLICA POPULAR DE BANGLADESH
    BB = 23  #  BARBADOS
    BY = 24  #  REPUBLICA DE BELARUS
    BE = 25  #  REINO DE BELGICA
    BZ = 26  #  BELICE
    BM = 27  #  BERMUDAS
    MM = 28  #  BIRMANIA
    BO = 29  #  REPUBLICA DE BOLIVIA
    BA = 30  #  BOSNIA HERZEGOVINA
    BW = 31  #  REPUBLICA DE BOTSWANA
    BR = 32  #  REPUBLICA FEDERAL DE BRASIL
    MY = 33  #  BRUNEI MALASIA
    BG = 34  #  REPUBLICA DE BULGARIA
    BI = 35  #  REPUBLICA DE BURUNDI
    BT = 36  #  REINO DE BUTAN
    CM = 37  #  REPUBLICA DE CAMERUN
    CA = 39  #  DOMINIO DE CANADA
    CO = 40  #  REPUBLICA DE COLOMBIA
    KR = 43  #  REPUBLICA DE COREA
    CI = 44  #  REPUBLICA DE COSTA DE MARFIL
    CR = 45  #  REPUBLICA DE COSTA RICA
    HR = 46  #  REPUBLICA DE CROACIA
    CU = 47  #  REPUBLICA DE CUBA
    CW = 48  #  CURAZAO
    TD = 49  #  REPUBLICA DE CHAD
    CZ = 50  #  REPUBLICA CHECA
    CL = 51  #  REPUBLICA DE CHILE
    CN = 52  #  REPUBLICA POPULAR CHINA
    DK = 54  #  REINO DE DINAMARCA
    EC = 56  #  REPUBLICA DEL ECUADOR
    EG = 57  #  REPUBLICA ARABE DE EGIPTO
    SV = 58  #  REPUBLICA DE EL SALVADOR
    AE = 59  #  EMIRATOS ARABES UNIDOS
    ES = 60  #  REINO DE ESPANA
    KW = 61  #  ESTADO DE KUWAIT
    QA = 62  #  ESTADO DE QATAR
    US = 63  #  ESTADOS UNIDOS DE NORTEAMERICA
    EE = 64  #  REPUBLICA DE ESTONIA
    ET = 65  #  REPUBLICA DEMOCRATICA FEDERAL DE ETIOPIA
    PH = 66  #  REPUBLICA DE LAS FILIPINAS
    FI = 67  #  REPUBLICA DE FINLANDIA
    FR = 68  #  REPUBLICA DE FRANCIA
    GA = 69  #  REPUBLICA DE GABON
    GM = 70  #  REPUBLICA DE LA GAMBIA
    GE = 71  #  GEORGIA
    GH = 72  #  REPUBLICA DE GHANA
    GI = 73  #  GIBRALTAR
    GD = 74  #  GRANADA
    GR = 75  #  GRECIA
    GL = 76  #  GROENLANDIA
    GU = 77  #  GUAM
    GT = 78  #  GUATEMALA
    GF = 79  #  GUAYANA FRANCESA
    GN = 80  #  GUINEA
    GQ = 81  #  GUINEA ECUATORIAL
    GY = 83  #  GUYANA
    HT = 86  #  REPUBLICA DE HAITI
    NL = 87  #  HOLANDA
    HN = 88  #  REPUBLICA DE HONDURAS
    HK = 89  #  HONG KONG
    HU = 90  #  HUNGRIA
    IN = 91  #  REPUBLICA DE INDIA
    ID = 92  #  REPUBLICA DE INDONESIA
    GB = 93  #  REINO UNIDO
    IQ = 94  #  REPUBLICA DE IRAK
    IR = 95  #  REPUBLICA ISLAMICA DE IRAN
    IE = 96  #  REPUBLICA DE IRLANDA
    KY = 97  #  ISLAS CAIMAN
    NF = 98  #  ISLA DE NORFOLK
    PM = 100  #  ISLA DE SAN PEDRO Y MIQUELIN
    IM = 101  #  ISLA DE MAN
    IS = 103  #  ISLANDIA
    IC = 105  #  ISLAS CANARIAS
    CK = 106  #  ISLAS COOK
    CC = 107  #  ISLAS DE COCOS O KELLING
    GG = 108  #  GUERNESEY
    FK = 109  #  ISLAS MALVINAS
    MH = 110  #  REPUBLICA DE LAS ISLAS MARSHALL
    SB = 112  #  ISLAS SALOMON
    TC = 113  #  ISLAS TURCAS Y CAICOS
    VG = 114  #  ISLAS VIRGENES BRITANICAS
    IL = 116  #  ESTADO DE ISRAEL
    IT = 117  #  REPUBLICA DE ITALIA
    JM = 118  #  JAMAICA
    JP = 119  #  JAPON
    JO = 120  #  REINO HASHEMITA DE JORDANIA
    KZ = 121  #  REPUBLICA DE KAZAJSTAN
    KE = 122  #  REPUBLICA DE KENYA
    KG = 123  #  REPUBLICA DE KIRGUISTAN
    KI = 124  #  REPUBLICA DE KIRIBATI
    LA = 127  #  REPUBLICA DEMOCRATICA POPULAR DE LAOS
    LS = 129  #  REINO DE LESOTHO
    LB = 130  #  REPUBLICA DEL LIBANO
    LR = 131  #  REPUBLICA DE LIBERIA
    LI = 133  #  PRINCIPADO DE LIECHENSTEIN
    LT = 134  #  REPUBLICA DE LITUANIA
    LU = 135  #  GRAN DUCADO DE LUXEMBURGO
    MO = 136  #  REGION ESPECIALADMINIOSTRATIVADEMACAODELAREPUBLICAPOPULARCHINA
    YU = 137  #  ANTIGUA REPUBLICA YUGOSLAVA DE MACEDONIA
    MG = 138  #  REPUBLICA DE MADAGASCAR
    MY = 140  #  MALASIA
    MW = 141  #  REPUBLICA DE MALAWI
    ML = 142  #  REPUBLICA DE MALI
    MT = 143  #  REPUBLICA DE MALTA
    MA = 144  #  REINO DE MARRUECOS
    MU = 145  #  REPUBLICA DE MAURICIO
    MR = 146  #  REPUBLICA ISLAMICA DE MAURITANIA
    MC = 148  #  PRINCIPADO DE MONACO
    MN = 149  #  MONGOLIA
    MS = 150  #  MONTSERRAT
    MZ = 151  #  REPUBLICA DE MOZAMBIQUE
    NA = 152  #  REPUBLICA DE NAMIBIA
    NR = 153  #  REPUBLICA DE NAURU
    NP = 154  #  ESTADO DE NEPAL
    NI = 156  #  REPUBLICA DE NICARAGUA
    NE = 268  #  NIGER
    NG = 158  #  REPUBLICA FEDERAL DE NIGERIA
    NU = 159  #  NIUE
    NO = 161  #  REINO DE NORUEGA
    NZ = 162  #  NUEVA ZELANDA
    OM = 163  #  SULTANATO DE OMAN
    PW = 164  #  REPUBLICA DE PALAOS
    PA = 165  #  REPUBLICA PANAMA
    PA = 166  #  REPUBLICA ISLAMICA DE PAQUISTAN
    PY = 167  #  REPUBLICA DE PARAGUAY
    PE = 168  #  REPUBLICA DEL PERU
    PN = 169  #  ISLAS PITCAIRN
    PF = 170  #  POLINESIA FRANCESA
    PL = 171  #  REPUBLICA DE POLONIA
    PT = 172  #  REPUBLICA DE PORTUGAL
    PR = 173  #  ESTADO LIBRE ASOCIADO DE PUERTO RICO
    TO = 175  #  REINO DE TONGA
    CV = 177  #  REPUBLICA DE CABO VERDE
    CY = 178  #  REPUBLICA DE CHIPRE
    MV = 181  #  REPUBLICA DE LAS MALDIVAS
    SC = 182  #  REPUBLICA DE SEYCHELLES
    TN = 183  #  REPUBLICA DE TUNEZ
    VU = 184  #  REPUBLICA DE VANUATU
    YE = 185  #  REPUBLICA DEL YEMEN
    DO = 186  #  REPUBLICA DOMINICANA
    MX = 187  #  MEXICO
    UY = 188  #  REPUBLICA ORIENTAL DE URUGUAY
    RW = 190  #  REPUBLICA DE RUANDA
    RO = 191  #  RUMANIA
    RU = 192  #  FEDERACION RUSA, RUSIA
    AS = 194  #  SAMOA AMERICANA
    VC = 197  #  SAN VICENTE Y LAS GRANADINAS
    SN = 199  #  REPUBLICA DE SENEGAL
    SL = 201  #  REPUBLICA DE SIERRA LEONA
    SK = 203  #  SLOVAKIA
    SI = 204  #  SLOVENIA
    SO = 205  #  SOMALIA
    LK = 206  #  REPUBLICA DEMOCRATICA SOCIALISTA DE SRI LANKA
    ZA = 207  #  REPUBLICA DE SUDAFRICA
    SD = 208  #  REPUBLICA DEL SUDAN
    SE = 209  #  REINO DE SUECIA
    CH = 210  #  CONFEDERACION HELVETICA, SUIZA
    SR = 211  #  REPUBLICA DE SURINAM
    TH = 212  #  REINO DE TAILANDIA
    TW = 213  #  REPUBLICA DE CHINA, TAIWAN
    TZ = 214  #  REPUBLICA UNIDA DE TANZANIA
    TJ = 215  #  REPUBLICA DE TAJIKISTAN
    TG = 216  #  REPUBLICA DE TOGO
    TK = 217  #  TOKELAU
    TT = 219  #  REPUBLICA DE TRINIDAD Y TOBAGO
    SH = 220  #  TRISTAN DE CUNHA
    TM = 222  #  TURKMENISTAN
    TR = 223  #  REPUBLICA DE TURQUIA
    TV = 224  #  TUVALU
    UA = 225  #  UCRANIA
    UG = 226  #  UGANDA
    UZ = 227  #  REPUBLICA DE UZBEKISTAN
    VE = 228  #  REPUBLICA BOLIVARIANA DE VENEZUELA
    VN = 229  #  REPUBLICA SOCIALISTA DE VIETNAM
    CD = 231  #  REPUBLICA DE ZAIRE
    ZM = 232  #  REPUBLICA DE ZAMBIA
    MM = 234  #  UNION DE MYANMAR
    KN = 235  #  SAN CRISTOBAL Y NIEVES
    SG = 236  #  REPUBLICA DE SINGAPURE
    WS = 237  #  SAMOA
    BF = 238  #  BURKINA FASO
    PS = 239  #  TERRITORIOS PALESTINOS
    CX = 240  #  ISLA DE CHRISTMAS
    KM = 241  #  COMORAS
    ER = 242  #  ERITREA
    FO = 243  #  ISLAS FAROE
    FJ = 244  #  FIYI
    MQ = 245  #  MARTINICA
    FM = 246  #  MICRONESIA
    MD = 247  #  MOLDOVA
    ME = 248  #  MONTENEGRO
    NC = 249  #  NUEVA CALEDONIA
    PS = 250  #  PALESTINA
    PG = 251  #  PAPUA NUEVA GUINEA
    SZ = 252  #  SUAZILANDIA
    ST = 253  #  SANTO TOME Y PRINCIPE
    RS = 254  #  SERBIA
    ZW = 255  #  ZIMBABUE
    AQ = 256  #  ANTARTIDA
    CD = 259  #  REPUBLICA DEMOCRATICA DEL CONGO
    AX = 257  #  ISLAS Åland
    BV = 258  #  ISLA BOUVET
    CP = 260  #  CLIPPERTON
    GP = 261  #  GUADALUPE
    GS = 262  #  GEORGIA DEL SUR E ISLAS SANDWICH DEL SUR
    HM = 263  #  ISLAS HEARD Y MCDONALD
    IO = 264  #  TERRITORIO BRITANICO DEL OCEANO INDICO
    JE = 265  #  JERSEY
    LV = 266  #  LETONIA
    MP = 267  #  ISLAS MARIANAS DEL NORTE
    NL = 269  #  PAISES BAJOS
    RE = 270  #  REUNION
    TF = 271  #  TERRITORIOS AUSTRALES FRANCESES
    UM = 272  #  ISLAS MENORES ALEJADAS DE LOS ESTADOS UNIDOS
    VA = 273  #  SANTA SEDE ESTADO DE LA CIUDAD DEL VATICANO
    WF = 274  #  WALLIS Y FUTUNA
    YT = 275  #  MAYOTTE
    WF = 274  #  WALLIS Y FUTUNA
    YT = 275  #  MAYOTTE


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
