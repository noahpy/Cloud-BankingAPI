
import pymysql as pmq
from logging import exception
from typing import Optional

"""
    Tool for developers to look into the database.
"""


class DataTool:

    __HOST = 'noah-banking.cjcipvue9uv5.us-east-1.rds.amazonaws.com'
    __USER = 'admin'
    __PASSWORD = 'noahadmin'
    __DATABASE = 'banking'

    def __init__(self):
        self.connection = None
        self.cursor = None
        try:
            self.connection = pmq.connect(host=DataTool.__HOST, user=DataTool.__USER, 
                                          password=DataTool.__PASSWORD)
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"USE {DataTool.__DATABASE}")
        except Exception:
            exception("[ERROR]: DataFetcher can not connect to the Database.")

    # close connection to the database
    def close_connection(self) -> bool:
        try:
            self.connection.close()
            return True
        except Exception:
            return False

    # Returns if there is an entry x in the given column and given table
    def exists(self,table:str, column:str, x) -> bool:
        try:
            self.connection.begin()
            self.cursor.execute(f"SELECT {column} from {table} WHERE {column}=%s", (x))
            data = self.cursor.fetchall()
            if len(data) > 0:
                return True
            else:
                return False
        except Exception:
            return False

    # Returns one IBAN of a given email
    def getIban(self, email:str) -> Optional[str]:
        try:
            self.connection.begin()
            self.cursor.execute(f"SELECT user_id from Authorization WHERE email=%s", (email))
            data = self.cursor.fetchall()
            user_id = data[0][0]
            data = self.cursor.execute(f"SELECT iban from Accounts WHERE user_id=%s", (user_id))
            iban = data[0][0]
            return iban
        except:
            return None


    # deletes every row of the given table
    def delete_from_all(self, table:str) -> bool:
        try:
            self.cursor.execute(f"DELETE FROM {table}")
            self.connection.commit()
            return True
        except Exception:
            return False


    # fetches all data from the given table
    def get_all(self, table:str) -> bool:
        try:
            self.connection.begin()
            self.cursor.execute(f"SELECT * from {table}")
            data = self.cursor.fetchall()
            return data
        except Exception:
            return ()


    




