
from dataQuery import DataFetcher
from ibanGenerator import IbanGenerator
import bcrypt
from typing import Optional, Tuple, Dict

"""
    Responsible for the Business Logic and Access Cotrol. Validates requests and executes
    them by using DataFetcher. 
    It hashes passwords by using bcrypt and unique salt, which the increases security againt 
    dictionary attacks.
    It is also a good way to defend against brute-force attacks, as the hashing
    is slow enough to make those attacks very time-consuming than when hashing with sha256.
"""

class BusinessController:

    def __init__(self):
        self.dataFetcher = DataFetcher()

    def dispose(self):
        """
        Should be called after usage to close the connection to the database
        """
        self.dataFetcher.close_connection()
    

    def __validate(self, email:str, password:str) -> Tuple[bool, int]:
        """
        Validate if the given email and password are authorized
        
        Parameters:
            email (str): email address the user
            password (str): password of the user

        Returns:
            -> (validity, user_id)
            validity (bool): Flag if request is valid
            user_id (int): Returns user_id when request is vaild, else -1
        """
        data = self.dataFetcher.get_rows_search("Authorization", "email", email)
        if not data:
            return False, -1
        pw_hash = data[0][0] 
        user_id = int(data[0][1])
        if bcrypt.checkpw(password.encode(),pw_hash):
            return True, user_id
        else: 
            # user_id can never be -1, as it is an unsigned int and auto_increment is activated
            return False, -1


    def createAccount(self, email:str, password:str, balance:int) -> Optional[str]:
        """
        Creates a new Account for a new email 

        Parameters:
            email (str): email address the user
            password (str): password of the user
            balance (int): inital balance of the account

        Returns:
            iban (Optional[str]): IBAN of the new account,
                                  None if creation was not successful
        """
        if self.dataFetcher.exists("Authorization", "email", email):
            return None
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        if not self.dataFetcher.add_row("Authorization", {"hash":hashed.decode(), "email":email}):
            return None
        data = self.dataFetcher.get_val_search("Authorization", "user_id", "email", email) 
        if not data:
            return None
        user_id = int(data[0][0])
        iban = IbanGenerator.generateIban()
        if self.dataFetcher.add_row("Accounts", {"iban":iban, "user_id":user_id, "balance":balance}):
            return iban
        else:
            return None



    def addAccount(self, email: str, password:str, balance:int) -> Optional[str]:
        """
        Creates an additional account for a known user

        Parameters:
            email (str): email address the user
            password (str): password of the user
            balance (int): inital balance of the account

        Returns:
            iban (Optional[str]): IBAN of the new account,
                                  None if creation was not successful
        """
        valid, user_id = self.__validate(email, password)
        if not valid:
            return None
        iban = IbanGenerator.generateIban()
        if self.dataFetcher.add_row("Accounts", {"iban":iban, "user_id":user_id, "balance":balance}):
            return iban
        else:
            return None


    def transferMoney(self, email: str, password:str, from_iban:str, to_iban:str, amount:int) -> bool:
        """
        Transfers money from current user to given iban account

        Parameters:
            email (str): email address the user
            password (str): password of the user
            from_iban (str): IBAN of the sending account
            to_iban (str): IBAN of the receiving account
            amount (int): amount of money which should be transfered

        Returns:
            successFlag (bool): Flag if transfer succeeded
        """
        if amount <= 0:
            return False
        valid, user_id = self.__validate(email, password)
        if not valid:
            return False
        data = self.dataFetcher.get_rows_search("Accounts", "user_id", user_id)
        _ , user_balance, _ = data[0]
        data = self.dataFetcher.get_val_search("Accounts", "balance", "iban", to_iban)
        if len(data) != 1:
            return False
        receiver_balance = data[0][0] + amount
        user_balance -= amount
        if not self.dataFetcher.update_value("Accounts", "balance", receiver_balance, "iban", to_iban):
            return False
        if not self.dataFetcher.update_value("Accounts", "balance", user_balance, "iban", from_iban):
            return False
        columnValueDict = {"from_iban":from_iban, "to_iban":to_iban, "amount":amount}
        if not self.dataFetcher.add_row("Transactions", columnValueDict):
            return False
        return True


    def retrieveBalance(self, email:str, password:str, iban:str) -> Optional[int]:
        """
        Retireves the balace of a given IBAN and user credentials

        Parameters:
            email (str): email address the user
            password (str): password of the user
            iban (str): IBAN of the account

        Returns:
            balance (Optional[int]): balance of the specified account,
                                     None if failed to retrieve the balance
        """
        valid, user_id = self.__validate(email, password)
        if not valid:
            return None
        # check if the account belongs to the user 
        data = self.dataFetcher.get_val_search("Accounts", "user_id", "iban", iban)
        if len(data) != 1:
            return None
        if data[0][0] != user_id:
            return None
        data = self.dataFetcher.get_val_search("Accounts", "balance", "iban", iban)
        if len(data) != 1:
            return None
        return data[0][0]


    def retrieveTransferHistory(self, email:str, password:str, iban:str) -> Optional[Dict]:
        """
        Retrieves the transfer history of an given iban and user credentials

        Parameters:
            email (str): email address the user
            password (str): password of the user
            iban (str): IBAN of the account

        Returns:
           transer_history (Optional[Dict]): 
                 If sucessful: 
                 Returns
                {
                    "sent": [(destination_iban, amount),..., (destination_iban, amount)],
                    "received": [(sender_iban, amount),..., (sender_iban, amount)]
                }

                - destination_iban (str): IBAN of the account where the user sent money
                - sender_iban (str): IBAN of the account from where the user received money
                - amount (int): amount of money which was transfered

                If not successful:
                Returns None
        """
        valid, user_id = self.__validate(email, password)
        if not valid:
            return None
        from_data = self.dataFetcher.get_rows_search("Transactions", "from_iban", iban)
        to_data = self.dataFetcher.get_rows_search("Transactions", "to_iban", iban)

        # check if the account belongs to the user 
        data = self.dataFetcher.get_val_search("Accounts", "user_id", "iban", iban)
        if len(data) != 1:
            return None
        if data[0][0] != user_id:
            return None

        # remove own iban, as it is not necessary data
        final_from_data = []
        for data in from_data:
            final_from_data.append((data[1],data[2]))
        final_to_data = []
        for data in to_data:
            final_to_data.append((data[0],data[2]))
        return {"sent":final_from_data, "received":final_to_data}

 

