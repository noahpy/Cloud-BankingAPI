
import requests
import unittest
from random import sample, randint, choice
import string 
import sys 
import os

sys.path.append(os.path.abspath("../../tools"))
from generateEmail import EmailGenerator
from queryTool import DataTool

sys.path.append(os.path.abspath("../../../src/business"))
from ibanGenerator import IbanGenerator

class TestApiInf(unittest.TestCase):

    HOST = "http://127.0.0.1"
    PORT = 5000
    ADDRESS = f"{HOST}:{PORT}/"

    # test creation / addition of accounts
    def testCreateAccount(self):
        print("\ntest creation of a new account...")
        dataTool = DataTool()
        email = EmailGenerator.generateEmail()
        password = ''.join(sample((string.ascii_letters+string.digits), randint(8,15)))
        balance = randint(-1000, 5000)
        headers = {'Content-Type': 'application/json'}
        body = {"email":email, "password":password, "balance":balance}
        response = requests.post(TestApiInf.ADDRESS+"createAccount", headers=headers, json=body)
        self.assertEqual(response.status_code, 200)
        if not response.json()["iban"]:
            self.fail("Did not receive correct iban-code")
        if not dataTool.exists("Accounts", "iban", response.json()["iban"]):
            self.fail("IBAN is not registered in database")
        print(f"Got an account: {response.json()['iban']}")

        print("\ntest adding a new account to user...")
        response = requests.post(TestApiInf.ADDRESS + "addAccount", headers=headers, json=body)
        self.assertEqual(response.status_code, 200)
        if not response.json()["iban"]:
            self.fail("Did not receive correct iban-code")
        if not dataTool.exists("Accounts", "iban", response.json()["iban"]):
            self.fail("IBAN is not registered in database")
        print(f"Got an additional account: {response.json()['iban']}")



    # test for error code with invalid inputs
    def testCreateAccountFail(self):
        # try create account with existing email
        print("\ntest creating accounts with invalid inputs...")
        balance = randint(-1000, 5000)
        headers = {'Content-Type': 'application/json'}
        body = {"email":"noah.schlenker2002@gmail.com", "password":"1123", "balance":balance}
        response = requests.post(TestApiInf.ADDRESS+"createAccount", headers=headers, json=body)
        self.assertEqual(response.status_code, 404)
        # try add account with unknwon email
        balance = randint(-1000, 5000)
        body = {"email":EmailGenerator.generateEmail(), "password":"ajJFJKE38", "balance":balance}
        response = requests.post(TestApiInf.ADDRESS+"addAccount", headers=headers, json=body)
        self.assertEqual(response.status_code, 404)


    def testMoneyTranser(self):
        dataTool = DataTool()
        receiver = choice(dataTool.get_all("Accounts"))
        amount = randint(10,500)
        knownEmail = "cleftcloud@outlook.com"
        knownPassword = "gk9n8JXD"
        knwonIban = "NL10205702772143466356350779626"
        headers = {'Content-Type': 'application/json'}
        
        print("\ntest money transfer with diffrent input combinations...")

        # test valid case
        body = {"email":knownEmail, "password":knownPassword,"from_iban":knwonIban, "to_iban": receiver[0], "amount":amount}
        response = requests.put(TestApiInf.ADDRESS+"transfer", headers=headers, json=body)
        self.assertEqual(response.status_code, 200)
        new_balance = tuple(filter(lambda x: x[0] == receiver[0],dataTool.get_all("Accounts")))[0][1]
        self.assertEqual(receiver[1]+amount, new_balance)

        # test with unknwon IBAN
        body = {"email":knownEmail, "password":knownPassword, "from_iban":knwonIban, "to_iban": IbanGenerator.generateIban(), "amount":amount}
        response = requests.put(TestApiInf.ADDRESS+"transfer", headers=headers, json=body)
        self.assertEqual(response.status_code, 404)

        # test with invalid amount
        body = {"email":knownEmail, "password":knownPassword, "from_iban":knwonIban, "to_iban": receiver[0], "amount":randint(-100000,0)}
        response = requests.put(TestApiInf.ADDRESS+"transfer", headers=headers, json=body)
        self.assertEqual(response.status_code, 404)

        # test with unknwon email
        body = {"email":EmailGenerator.generateEmail(), "password":knownPassword, "from_iban":knwonIban, "to_iban": receiver[0], "amount":amount}
        response = requests.put(TestApiInf.ADDRESS+"transfer", headers=headers, json=body)
        self.assertEqual(response.status_code, 404)

        # test wit wrong password
        body = {"email":knownEmail, "password":"wrong Password", "from_iban":knwonIban, "to_iban": receiver[0], "amount":amount}
        response = requests.put(TestApiInf.ADDRESS+"transfer", headers=headers, json=body)
        self.assertEqual(response.status_code, 404)


    def testRetrieveBalance(self):
        dataTool = DataTool()
        knownEmail = "cleftcloud@outlook.com"
        knownPassword = "gk9n8JXD"
        knwonIban = "NL10205702772143466356350779626"
        headers = {'Content-Type': 'application/json'}

        print("\ntest retrieving balance with diffrent input combinations...")
        
        # test valid case
        knwonBalance = tuple(filter(lambda x: x[0] == knwonIban, dataTool.get_all("Accounts")))[0][1]
        body = {"email":knownEmail, "password":knownPassword, "iban": knwonIban}
        response = requests.get(TestApiInf.ADDRESS+"stats", headers=headers, json=body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["balance"], knwonBalance)

        # test with other known IBAN 
        otherIban = choice(dataTool.get_all("Accounts"))[0]
        body = {"email":knownEmail, "password":knownPassword, "iban": otherIban}
        response = requests.get(TestApiInf.ADDRESS+"stats", headers=headers, json=body)
        self.assertEqual(response.status_code, 404)

        # test with unknwon email
        body = {"email":EmailGenerator.generateEmail(), "password":knownPassword, "iban": knwonIban}
        response = requests.get(TestApiInf.ADDRESS+"stats", headers=headers, json=body)
        self.assertEqual(response.status_code, 404)

        # test with wrong password
        body = {"email":knownEmail, "password":"wrong Password", "iban": knwonIban}
        response = requests.get(TestApiInf.ADDRESS+"stats", headers=headers, json=body)
        self.assertEqual(response.status_code, 404)

        # test with unknwon IBAN 
        body = {"email":knownEmail, "password":knownPassword, "iban": IbanGenerator.generateIban()}
        response = requests.get(TestApiInf.ADDRESS+"stats", headers=headers, json=body)
        self.assertEqual(response.status_code, 404)


    def testRetrieveTransferHistory(self):
        """
            CAUTION! This test assumes that creating accounts and transfering money is working!

            This test creates a new account, which then makes randomly often generated transfers
            with a known account. After that, the transfer history is requested and tested on its 
            correctness.
        """
        dataTool = DataTool()
        knownEmail = "cleftcloud@outlook.com"
        knownPassword = "gk9n8JXD"
        knwonIban = "NL10205702772143466356350779626"

        print("\ntest retrieving transfer history...")

        # create test subject account 
        email = EmailGenerator.generateEmail()
        password = ''.join(sample((string.ascii_letters+string.digits), randint(8,15)))
        balance = randint(-1000, 5000)
        headers = {'Content-Type': 'application/json'}
        body = {"email":email, "password":password, "balance":balance}
        response = requests.post(TestApiInf.ADDRESS+"createAccount", headers=headers, json=body)
        iban = response.json()["iban"]
        
        print("generate and execute random transfers...")
        # generate random transfer history 
        transfer_history = []
        for i in range(randint(15,30)):
            amount = randint(20,2000)
            if randint(0,1) == 1:
                body = {"email":email, "password":password,"from_iban": iban, "to_iban":knwonIban, "amount":amount}
                if requests.put(TestApiInf.ADDRESS+"transfer", headers=headers, json=body).status_code == 200:
                    transfer_history.append((iban, knwonIban, amount))
            else:
                body = {"email":knownEmail, "password":knownPassword,"from_iban": knwonIban, "to_iban":iban, "amount":amount}
                if requests.put(TestApiInf.ADDRESS+"transfer", headers=headers, json=body).status_code == 200:
                    transfer_history.append((knwonIban, iban, amount))
            
        print("check validity of requested transfer history...")
        # request transfer history and check for correctness
        body = {"email":email, "password":password, "iban": iban}
        response = requests.get(TestApiInf.ADDRESS+"history", headers=headers, json=body)
        for received in response.json()["received"]:
            if (received[0], iban, received[1]) in transfer_history:
                transfer_history.remove((received[0], iban, received[1]))
            else:
                self.fail("A received transfer was found which never happened")
        for sent in response.json()["sent"]:
            if (iban, sent[0], sent[1]) in transfer_history:
                transfer_history.remove((iban, sent[0], sent[1]))
            else:
                self.fail("A sent transfer was found which never happened")
        self.assertEqual(transfer_history, [])



        

        








        










	
















        
        

  

if __name__ == "__main__":
    unittest.main()
