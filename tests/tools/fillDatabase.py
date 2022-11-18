import os
import sys
from random import randint

sys.path.append(os.path.abspath("../../src/business/"))

from dataQuery import DataFetcher
from ibanGenerator import IbanGenerator

ADD_AMOUNT = 500

dataFetcher = DataFetcher()

for index in range(ADD_AMOUNT):
    iban = IbanGenerator.generateIban()
    dictval = {"iban":iban, "balance":randint(-1000,5000), "user_id":randint(1,20000)}
    print(index, dictval)
    dataFetcher.add_row("Accounts", dictval)

data = dataFetcher.get_all("Accounts")
print(data)

dataFetcher.close_connection()
