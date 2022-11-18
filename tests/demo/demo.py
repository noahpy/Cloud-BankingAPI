
import random
import requests
import sys 
import os

sys.path.append(os.path.abspath("../tools"))
from generateEmail import EmailGenerator

HOST = "http://127.0.0.1"
PORT = 5000
ADDRESS = f"{HOST}:{PORT}/"

headers = {'Content-Type': 'application/json'}


WELCOME = """
Welcome to this demo program!
In this program, you are going to be walked through 
every functionality of this Banking API!
"""

CREATE_ACCOUNT = """
First, let us create you a new account!
For that, we need your email address, a password and the 
inital balance of your bank account.
Enter just 'g' if you want to geneate an unique address.
"""

CREATE_ACCOUNT_READY = """
Now, you are ready to create your account!
After creating your account, you will receive your unique IBAN.
Later on, IBANs are used for transfering money between accounts.
"""

CREATE_ANOTHER_ACCOUNT = """
You can also create multiple bank accounts with 
a single email address. 
We again just need an inital balance.
"""

BOB_ACCOUNT = """
Now, we create another account for Bob,
with who you are going to transfer some of your money around.
"""

TRANSFER_MONEY = """
Let us now transfer money to Bob's account!
For that, we need the source IBAN, the destination IBAN and the transfer amount.
The destination IBAN is automatically set to the IBAN of Bob's account.
"""

RETRIEVE_BALANCE = """
Now, you may want to know your new balance of your accounts.
Let us retrieve the balances of both of your accounts!
For this, we need your IBANs as inputs, but here it is going to 
be send automatically.
"""

RECEIVE_MONEY = """
Seems like you received money from Bob!
Let us check your balances again!
"""

TRANSER_HISTORY = """
You can also retrieve your transfer history.
For that, we need to specify the account of which we want the history from.
"""


input(WELCOME)

print(CREATE_ACCOUNT)
email = input("Your Email: ").strip()
if email == "g":
    email = EmailGenerator.generateEmail()

print(f"Your email address is: {email}")

password = input("Your password: ")
while not password:
    password = input("Your password: ")

balance = None
while balance is None:
    try:
        balance = int(input("Your inital balance: "))
    except:
        pass

input(CREATE_ACCOUNT_READY)
print("Creating account...")

body = {"email":email, "password":password, "balance":balance}
response = requests.post(ADDRESS+"createAccount", headers=headers, json=body)
if response.status_code != 200:
    print("Could not create account...")
    exit()
iban = response.json()["iban"]

input(f"Your IBAN: {iban}")

print(CREATE_ANOTHER_ACCOUNT)
scd_balance = None
while scd_balance is None:
    try:
        scd_balance = int(input("Your inital balance: "))
    except:
        pass
print(f"Creating second account with inital amount {scd_balance}...")
body = {"email":email, "password":password, "balance":scd_balance}
response = requests.post(ADDRESS+"addAccount", headers=headers, json=body)
if response.status_code != 200:
    print("Could not create account...")
    exit()
scd_iban = response.json()["iban"]


input(f"Your second IBAN: {scd_iban}")

print(BOB_ACCOUNT)
bob_email = EmailGenerator.generateEmail()
bob_password = "ajtk35"
bob_balance = 10000
body = {"email":bob_email, "password":bob_password, "balance":bob_balance}
response = requests.post(ADDRESS+"createAccount", headers=headers, json=body)
if response.status_code != 200:
    print("Could not create account for Bob...")
    exit()
bob_iban = response.json()["iban"]
print(f"Bob's account:\n     IBAN: {bob_iban}\n     balance: {bob_balance}")


print(TRANSFER_MONEY)
print(f"Specify source account:\n     - (f)irst: {iban}\n     - (s)econd: {scd_iban}")
src_choice = ""
while src_choice not in ["f", "s"]:
    src_choice = input("Your choice: ")
if src_choice == "f":
    src_iban = iban
else:
    src_iban = scd_iban

amount = None
while amount is None:
    try:
        amount = int(input("Transfer amount: "))
    except:
        pass


print(f"Transferring: {src_iban} --- {amount} ---> {bob_iban}") 

body = {"email":email, "password":password,"from_iban":src_iban, "to_iban": bob_iban, "amount":amount}
response = requests.put(ADDRESS+"transfer", headers=headers, json=body)
if response.status_code != 200:
    print("Failed to transfer...")
    exit()

print("Transfer was successful!")

input(RETRIEVE_BALANCE)


body = {"email":email, "password":password, "iban": iban}
response = requests.get(ADDRESS+"stats", headers=headers, json=body)
if response.status_code != 200:
    print("Could not retrieve balance...")
    exit()
f_balance = response.json()["balance"]

body = {"email":email, "password":password, "iban": scd_iban}
response = requests.get(ADDRESS+"stats", headers=headers, json=body)
if response.status_code != 200:
    print("Could not retrieve balance...")
    exit()
scd_balance = response.json()["balance"]


print(f"Your new balances:\n     {iban}: {f_balance}\n     {scd_iban}: {scd_balance}")

body = {"email":bob_email, "password":bob_password, "iban": bob_iban}
response = requests.get(ADDRESS+"stats", headers=headers, json=body)
if response.status_code != 200:
    print("Could not retrieve balance from Bob...")
    exit()
print(f"\nBob's new balance:\n     {bob_iban}: {response.json()['balance']}")

amount = random.randint(1,5)*1000
body = {"email":bob_email, "password":bob_password,"from_iban":bob_iban, "to_iban": iban, "amount": amount}
response = requests.put(ADDRESS+"transfer", headers=headers, json=body)
if response.status_code != 200:
    print("Failed to transfer...")
    exit()

print(f"Transferring {iban} <--- {amount} --- {bob_iban}")

input(RECEIVE_MONEY)

body = {"email":email, "password":password, "iban": iban}
response = requests.get(ADDRESS+"stats", headers=headers, json=body)
if response.status_code != 200:
    print("Could not retrieve balance...")
    exit()
f_balance = response.json()["balance"]

body = {"email":email, "password":password, "iban": scd_iban}
response = requests.get(ADDRESS+"stats", headers=headers, json=body)
if response.status_code != 200:
    print("Could not retrieve balance...")
    exit()
scd_balance = response.json()["balance"]

print(f"Your new balances:\n     {iban}: {f_balance}\n     {scd_iban}: {scd_balance}")

input(TRANSER_HISTORY)
print(f"Specify account:\n     - (f)irst: {iban}\n     - (s)econd: {scd_iban}\n")
src_choice = ""
while src_choice not in ["f", "s"]:
    src_choice = input("Your choice: ")
if src_choice == "f":
    src_iban = iban
else:
    src_iban = scd_iban


body = {"email":email, "password":password, "iban": src_iban}
response = requests.get(ADDRESS+"history", headers=headers, json=body)
for received in response.json()["received"]:
    print(f"{src_iban} <--- {received[1]} --- {received[0]}")
for sent in response.json()["sent"]:
    print(f"{src_iban} --- {sent[1]} ---> {sent[0]}")


