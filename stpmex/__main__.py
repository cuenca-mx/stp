"""
CLI para enviar órdenes a STP.
"""
import argparse
from clabe.banks import BANKS, BANK_NAMES
import json
import stpmex
from stpmex import Orden

DEFAULT_FILE_NAME = 'stp.config'


def config():
    """
    Crea un archivo de configuración con las credenciales de STP para poder
    enviar órdenes posteriormente. PRECAUCIÓN: El archivo se guarda sin
    cifrar y en la ubicación donde se encuentre la línea de comandos en ese
    momento.
    :return:
    """
    print('Configuring connection')
    print('It will create a stp.config file')

    pk_file = input('Route to private key: ')
    with open(pk_file) as fp:
        pk_value = fp.read()
    configuration = {
        'wsdl': input('WSDL: '),
        'private_key': pk_value,
        'pkey_passphrase': input('Private key passphrase: '),
        'empresa': input('Empresa: '),
        'prefijo': input('Prefijo: ')
    }
    use_proxy = input('Wish to use a proxy? (y/n): ').lower() == 'y'
    if use_proxy:
        configuration['proxy'] = input('Proxy: ')
        configuration['user'] = input('User: ')
        configuration['password'] = input('Password: ')

    with open(DEFAULT_FILE_NAME, 'w') as outfile:
        json.dump(configuration, outfile)

    print("Done...")


def order():
    """
    Crea una nueva orden para enviar a STP
    :return:
    """
    try:
        with open(DEFAULT_FILE_NAME, 'r') as f:
            config = json.load(f)
    except IOError:
        print("No configuration file found, use first: stpmex config")
        return

    stpmex.configure(wsdl_path=config['wsdl'], empresa=config['empresa'],
                     priv_key=config['private_key'],
                     priv_key_passphrase=config['pkey_passphrase'],
                     prefijo=config['prefijo'],
                     proxy=None if 'proxy' not in config else config['proxy'],
                     proxy_user=None if 'user' not in config
                     else config['user'],
                     proxy_password=None if 'password' not in config
                     else config['password'],
                     )

    print("Connection established")

    order = Orden()
    order.institucionOperante = list(BANK_NAMES.keys())[
    list(BANK_NAMES.values()).index('STP')]
    order.nombreBeneficiario = input('Nombre del beneficiario: ')
    order.cuentaBeneficiario = input('CLABE del beneficiario: ')
    order.institucionContraparte = input('Institución de contraparte: ')
    order.conceptoPago = input('Concepto de pago: ')
    order.monto = float(input('Monto: '))  # I assume you won't put a str here
    rfc = input('RFC o CURP de beneficiario (opcional): ')
    if rfc:
        order.rfcCurpBeneficiario = rfc
    num_reference = input('Referencia númerica (opcional): ')
    if num_reference:
        order.referenciaNumerica = num_reference
    track_code = input('Clave de rastreo (opcional): ')
    if track_code:
        order.claveRastreo = track_code

    print("Sending order....")
    r = order.registra()

    print(r)
    print("Finished")


def main():
    """
    Función principal, recibe como argumento la función a utilizar
    :return:
    """
    parser = argparse.ArgumentParser(description='Creates an order to STP')
    parser.add_argument('option', choices=['config', 'order'],
                        help="'config' to configure the client,"
                             "'order' for creating a new order")
    args = parser.parse_args()
    if args.option == 'config':
        config()
    if args.option == 'order':
        order()


if __name__ == '__main__':
    main()
