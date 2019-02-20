from enum import Enum


class AccountType(Enum):
    DEBIT_CARD = 3
    PHONE_NUMBER = 10
    CLABE = 40


class Prioridad(Enum):
    normal = 0
    alta = 1
