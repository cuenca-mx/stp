## STP client python3 client library

[![Build Status](https://travis-ci.com/cuenca-mx/stpmex-python.svg?branch=master)](https://travis-ci.com/cuenca-mx/stpmex-python)


Cliente para el servicio SOAP de STP

Demo wsdl: https://demo.stpmex.com:7024/speidemo/webservices/SpeiActualizaServices?wsdl


**Requerimientos**

Python v3 o superior.

**Instalación**

Se puede instalar desde Pypi usando

```
pip install stpmex
```

**Test**

Para ejecutar los test utlizando el archivo Makefile

```
$ make test
```

**Uso básico**

Comenzar configurando el cliente con las credenciales

``` Python
import stpmex
```

Obtener la llave PEM

``` Python
PKEY_ADD = '/Users/test/prueba-key.pem'
with open(PKEY_ADD) as fp:
    private_key = fp.read()
```

Utilizar configure() para configurar las credenciales a utilizar

``` Python
stpmex.configure(wsdl_path='https://demo.stpmex.com:7024/speidemo/webservices/SpeiActualizaServices?wsdl', empresa='PRUEBA', priv_key=private_key, priv_key_passphrase='12345678', prefijo=9999)
```

Para crear una nueva orden, crear una instancia de Orden y llamar registra()

``` Python
orden = stpmex.Orden(conceptoPago='Prueba', institucionOperante=stpmex.types.Institucion.STP.value, cuentaBeneficiario='846180000400000001', institucionContraparte=846, monto=1234, nombreBeneficiario='Benito Juárez')
orden.registra()
```
