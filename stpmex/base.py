from base64 import b64encode
from OpenSSL import crypto

STP_EMPRESA = None
STP_PRIVKEY = None
STP_PRIVKEY_PASSPHRASE = None
STP_PREFIJO = None
SIGN_DIGEST = 'RSA-SHA256'
ACTUALIZA_CLIENT = None
DEBUG_MODE = False
HISTORY = None


def _join_fields(obj, fieldnames):
    fields = []
    for name in fieldnames:
        if name in ['monto', 'iva'] and not getattr(obj, name) in ['', None]:
            field = float(getattr(obj, name))
            field = f'{field:.2f}'
        else:
            field = getattr(obj, name) or ''
        fields.append(str(field))
    return ('||' + '|'.join(fields) + '||').encode('utf-8')


def _validate(field, field_value, validation, validation_value):
    """
        Evalua si el valor de un campo es válido y devuelve un mensaje de error
    :param field: Nombre del campo
    :param field_value: Valor del campo
    :param validation: Tipo de validación a realizar
    :param validation_value: Valor a validar
    :return:
    """
    if validation == 'required' and validation_value and not field_value:
        return 'Field {} is required'.format(field)
    if validation == 'maxLength' and validation_value < len(str(field_value)):
        return 'Length of field {} must be lower than {}'\
            .format(field, validation_value)
    return None


class Resource:
    __fieldnames__ = None
    __object__ = None
    __type__ = None
    __validations__ = None
    _defaults = {}

    def __init__(self, **kwargs):
        for default, value in self._defaults.items():
            if default not in kwargs:
                if callable(value):
                    kwargs[default] = value()
                else:
                    kwargs[default] = value
        self.__object__ = ACTUALIZA_CLIENT.get_type(self.__type__)(**kwargs)
        self.empresa = STP_EMPRESA
        self.firma = None

    def __dir__(self):
        return dir(super(Resource, self)) + dir(self.__object__)

    def __dict__(self):
        return {r: self.__getattr__(r) for r in self.__fieldnames__}

    def __eq__(self, other):
        return all(getattr(self, name) ==
                   getattr(other, name) for name in self.__fieldnames__)

    def __getattr__(self, item):
        if item.startswith('_'):
            return self.__getattribute__(item)
        return getattr(self.__object__, item)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        indent = ' ' * 4
        rv = f'{self.__class__.__name__}(\n'
        for name in self.__fieldnames__:
            rv += f'{indent}{name}={repr(getattr(self, name))},\n'
        rv += ')'
        return rv

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super(Resource, self).__setattr__(key, value)
        else:
            setattr(self.__object__, key, value)

    def __str__(self):
        return self.__object__.__str__()

    @property
    def _joined_fields(self):
        return _join_fields(self, self.__fieldnames__)

    def _compute_signature(self):
        signature = crypto.sign(STP_PRIVKEY, self._joined_fields, SIGN_DIGEST)
        return b64encode(signature).decode('ascii')

    def _is_valid_field(self, field):
        """
            Obtiene el campo a ser evaluado y el diccionario de validaciones
            que deban hacerse
        :param field: Campo a evaluar
        :return: Lista de errores encontrados en este campo
        """
        # Validaciones que aplican en este campo
        vals = self.__validations__[field]
        return [_validate(field, getattr(self, field), r, vals[r])
                for r in vals]

    def _is_valid(self):
        """
            Por todos los campos a ser validados, ejecuta la función
            _is_valid_field y devuelve todos los errores
        :return: None si no hay errores, de otra forma lanza una
            excepción con la lista de errores
        """
        errors = list(filter((lambda x: x is not None),
                             [error for errors in
                              map((lambda r: self._is_valid_field(r)),
                                  self.__validations__)
                              for error in errors]))
        if len(errors) > 0:
            raise ValueError(",".join(errors))
        return None

    def _invoke_method(self, method):
        res = ACTUALIZA_CLIENT.service[method](self.__object__)
        return res
