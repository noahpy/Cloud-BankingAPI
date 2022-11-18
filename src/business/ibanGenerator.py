from random import choice, randint
from string import digits
from dataQuery import DataFetcher

"""
    Generates a (to the database) unique IBAN Code when calling generateIban(). 
    Generated IBANs are simular to the real world codes, but do not follow all rules.
"""

class IbanGenerator:
    
    #generally, iban has a range of 22 to 34 characters.
    #note: private static variables are not easily visible, but not completely private.
    #      -> You could acces it with IbanGenerator._IbanGenerator__CHARACTERLIMIT
    __CHARACTERLOWERLIMIT = 22
    __CHARACTERUPPERLIMIT = 34
    #generally, country codes are 2 charcters, but 3 characters are also possible.
    __COUNTYCODES = ("DE", "FR", "JP", "NL", "NP", "PH", "ES", "CH", "GB", "US")

    @staticmethod
    def generateIban() -> str:
        keep_generating = True
        result = None
        dataFetcher = DataFetcher()
        while keep_generating:
            result =  choice(IbanGenerator.__COUNTYCODES)
            str_len = randint(IbanGenerator.__CHARACTERLOWERLIMIT-len(result), 
                              IbanGenerator.__CHARACTERUPPERLIMIT-len(result)+1)
            for i in range(str_len):
                result += choice(digits)
            keep_generating = dataFetcher.exists("Accounts", "iban", result)
        dataFetcher.close_connection()
        return result

 
