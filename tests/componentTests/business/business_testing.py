
import unittest
import os 
import sys
from random import sample, randint
import string

sys.path.append(os.path.abspath("../../tools"))
from generateEmail import EmailGenerator

sys.path.append(os.path.abspath("../../../src/business/"))
from businessController import BusinessController
from ibanGenerator import IbanGenerator

"""
    Tests every given method of the business layer interface, BusinessController,
    by walking through a randomly generated scenario and executing with invalid inputs.
"""

class TestBusinessLayer(unittest.TestCase):

    def testScenario(self):
        businessController = BusinessController()

        # test creation of accounts with unique email addresses 
        alice_email = EmailGenerator.generateEmail()
        alice_password = ''.join(sample((string.ascii_letters+string.digits), randint(8,15)))
        alice_balance = randint(-1000, 5000)
        alice_iban = businessController.createAccount(alice_email, alice_password, alice_balance)
        if alice_iban == None:
            self.fail("Not able to create new account, despite having a unique email")
        print(f"\nCreated Alice account:\nemail: {alice_email}\npassword: {alice_password}\nIBAN:{alice_iban}\nbalance:{alice_balance}\n")

        bob_email = EmailGenerator.generateEmail()
        bob_password = ''.join(sample((string.ascii_letters+string.digits), randint(8,15)))
        bob_balance = randint(-1000, 5000)
        bob_iban = businessController.createAccount(bob_email, bob_password, bob_balance)
        if bob_iban == None:
            self.fail("Not able to create new account, despite having a unique email")
        print(f"Created Bob account:\nemail: {bob_email}\npassword: {bob_password}\nIBAN:{bob_iban}\nbalance:{bob_balance}\n")

        # test transferal of money, correct balance and transfer history, by making random transfers
        transfer_history = []
        test_amount = randint(5,10)
        for i in range(test_amount):
            transfer_amount = randint(10,2000)
            # send from alice to bob
            if randint(0,1) == 1:
                result = businessController.transferMoney(alice_email, alice_password, alice_iban, bob_iban, transfer_amount)
                if not result:
                    self.fail("Could not transfer money depite valid inputs")
                bob_balance += transfer_amount
                alice_balance -= transfer_amount

                # check if the balances are right
                if alice_balance != businessController.retrieveBalance(alice_email, alice_password, alice_iban):
                    self.fail("Alice: Did not return the right balance after Transfer")
                if bob_balance != businessController.retrieveBalance(bob_email, bob_password, bob_iban):
                    self.fail("Bob: Did not return the right balance after Transfer")

                transfer_history.append((alice_iban, bob_iban, transfer_amount))
                print(f"Sent {transfer_amount} from Alice to Bob!\n")
            #send from bob to alice
            else:
                result = businessController.transferMoney(bob_email, bob_password, bob_iban, alice_iban, transfer_amount)
                if not result:
                    self.fail("Could not transfer money depite valid inputs")
                bob_balance -= transfer_amount
                alice_balance += transfer_amount

                # check if the balances are right 
                if alice_balance != businessController.retrieveBalance(alice_email, alice_password, alice_iban):
                    self.fail("Alice: Did not return the right balance after Transfer")
                if bob_balance != businessController.retrieveBalance(bob_email, bob_password, bob_iban):
                    self.fail("Bob: Did not return the right balance after Transfer")

                transfer_history.append((bob_iban, alice_iban, transfer_amount))
                print(f"Sent {transfer_amount} from Bob to Alice!\n")
        #test if transfer history matches 
        alice_transfer_data = businessController.retrieveTransferHistory(alice_email, alice_password, alice_iban)
        bob_transfer_data = businessController.retrieveTransferHistory(bob_email, bob_password, bob_iban)
        for transfer in transfer_history:
            print(f"checking transfer: {transfer[0]} --- {transfer[2]} ---> {transfer[1]}")
            if transfer[0] == alice_iban:
                if (bob_iban, transfer[2]) in alice_transfer_data["sent"]:
                    alice_transfer_data["sent"].remove((bob_iban, transfer[2]))
                else:
                    self.fail("Sent transfer of Alice is missing")
                if (alice_iban, transfer[2]) in bob_transfer_data["received"]:
                    bob_transfer_data["received"].remove((alice_iban, transfer[2]))
                else:
                    self.fail("Received tranfer of Bob is missing")
            else:
                if (bob_iban, transfer[2]) in alice_transfer_data["received"]:
                    alice_transfer_data["received"].remove((bob_iban, transfer[2]))
                else:
                    self.fail("Received transfer of Alice is missing")
                if (alice_iban, transfer[2]) in bob_transfer_data["sent"]:
                    bob_transfer_data["sent"].remove((alice_iban, transfer[2]))
                else:
                    self.fail("Sent tranfer of Bob is missing")

        # test creating additional account for known user 
        new_balance = randint(-1000, 5000)
        new_iban = businessController.addAccount(alice_email, alice_password, new_balance)
        if new_iban is None:
            self.fail("Alice: Could not create additional account, despite valid inputs")
        print(f"\nCreated additional account for Alice:\niban: {new_iban}\nbalance: {new_balance}")

        businessController.dispose()

    # test invalid attempt of account creating / adding 
    def testInvalidAccountCreation(self):
        print("\nTesting invalid account creation...")
        businessController = BusinessController()
        self.assertEqual(businessController.createAccount("noah.schlenker2002@gmail.com", "!", 20), None)
        self.assertEqual(businessController.addAccount(EmailGenerator.generateEmail(), "!", 20), None)
        businessController.dispose()

    # test invalid attempts with unkown Email
    def testUnknownEmail(self):
        print("\nTest attempts with invalid email...")
        businessController = BusinessController()
        unknwonEmail = EmailGenerator.generateEmail()
        knownIban = 'US05918249515412069724886755'
        self.assertEqual(businessController.transferMoney(unknwonEmail, "12345",knownIban, knownIban, 20), False)
        self.assertEqual(businessController.retrieveBalance(unknwonEmail, "12345", knownIban), None)
        self.assertEqual(businessController.retrieveTransferHistory(unknwonEmail, "12345", knownIban), None)
        businessController.dispose()

    # test invalid attempts with unkown iban 
    def testUnknownIban(self):
        print("\nTest attempts with invalid iban...")
        businessController = BusinessController()
        knownEmail = "mcdonald.wack@outlook.com"
        knownPassword = "SM5dNFkK"
        knownIban = 'US05918249515412069724886755'
        unknownIban = IbanGenerator.generateIban()
        self.assertEqual(businessController.transferMoney(knownEmail, knownPassword, knownIban, unknownIban, 20), False)
        self.assertEqual(businessController.retrieveBalance(knownEmail, knownPassword, unknownIban), None)
        self.assertEqual(businessController.retrieveTransferHistory(knownEmail, knownPassword, unknownIban), None)
        businessController.dispose()

    def testInvalidTransfer(self):
        print("\n Try to transfer a negative amount of money...")
        businessController = BusinessController()
        knownEmail = "cleftcloud@outlook.com"
        knownPassword = "gk9n8JXD"
        knownIban = "NL10205702772143466356350779626"
        knownReceiverIban = 'US05918249515412069724886755'
        invalidAmount = randint(-100000, 0)
        self.assertEqual(businessController.transferMoney(knownEmail, knownPassword, knownIban, knownReceiverIban, invalidAmount), False)
        businessController.dispose()







if __name__ == "__main__":
    unittest.main()
