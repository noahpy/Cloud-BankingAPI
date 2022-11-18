
import pymysql as pmq
from logging import exception

"""
    Fetches and looks up data in the specified Database by generating SQL Queries.
    To ensure clean usage, one should call the close_connection() before dispsal.
    Its methods will return False if the Database is not available.(
"""

class DataFetcher:

    # NOTE: These are not truly private attributes!
    __HOST = 'deleted'
    __USER = 'admin'
    __PASSWORD = 'admin'
    __DATABASE = 'banking'


    #NOTE: 
    #   These methods are now SQL Injection-Safe, as I introduced parametrized Queries.
    #   Beferoe that, get_rows_search("Authorization", "email", "' OR '1' = '1") would 
    #   return every users email with its hash!
    #   Some arguments like table and column are not parametrized, but it is still safe, as
    #   those arguments are not by the user but by the BusinessController.

    # Tries to connect to the Database. If failed, it will log an exception. 
    # Further methods will not raise any Exceptions, instead always return False if there is no connection.
    def __init__(self):
        self.connection = None
        self.cursor = None
        try:
            self.connection = pmq.connect(host=DataFetcher.__HOST, user=DataFetcher.__USER, 
                                          password=DataFetcher.__PASSWORD)
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"USE {DataFetcher.__DATABASE}")
        except Exception:
            exception("[ERROR]: DataFetcher can not connect to the Database.")


    def close_connection(self) -> bool:
        """
        Closes connection to the database
        Should always be called after using DataFetcher

        Returns:
            successFlag (bool): Flag if the closing of the connection was successful
        """
        try:
            self.connection.close()
            return True
        except Exception:
            return False


    def exists(self,table:str, column:str, x) -> bool:
        """
        Queries if there is an entry x in the given table and column

        Returns:
           existsFlag (bool): True if entry was found, else False 
        """
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


    def get_rows_search(self, table:str, column:str, x) -> tuple:
        """
        Returns all the rows on the given table, which have an entry x in the given column

        Parameters:
            table (str): table name 
            column (str): column name 
            x (Object): queried entry

        Returns:
            --> (row1, row2, ... , rowN)
                row: (entry1, entry2, ... , entryM)
        """
        try:
            self.connection.begin()
            self.cursor.execute(f"SELECT * from {table} WHERE {column}=%s", (x))
            data = self.cursor.fetchall()
            return data
        except Exception:
            return ()

    
    def get_val_search(self, table:str, selectCol: str, searchCol:str, x) -> tuple:
        """
        Queries for rows in the given table, which have an entry x in the search column.
        Then returns the values of the select column of those rows.

        Parameters:
            table (str): table name
            selectCol (str): select column name 
            searchCol (str): queried column name 
            x (Object): queried entry

        Returns:
            --> ((val1), (val2), ... , (valN))
                val: Values of the select column of the rows which fulfill the condition
        """
        try:
            self.connection.begin()
            self.cursor.execute(f"SELECT {selectCol} from {table} WHERE {searchCol}=%s", (x))
            data = self.cursor.fetchall()
            return data
        except Exception:
            return ()
    
 
    def add_row(self, table:str, valdict:dict) -> bool:
        """
        Adds a new row to the given table

        Parameters:
            table (str): table name 
            valdict (Dict): a dictionary with the Format:
                            {
                                column_name : new_value
                            }
        Returns:
            successFlag (bool): True if adding a new row was successful, else False
        """
        columns = "("
        values = "("
        for index, pair in enumerate(valdict.items()):
            col, val = pair
            columns += str(col) 
            # parametrize values so that the sole input is valdict
            values += f"%({col})s"
            if index < len(valdict.items())-1:
                columns += ","
                values += ","
            else:
                columns += ")"
                values += ")"
        sql = f"INSERT INTO {table} {columns} VALUES {values};"
        try:          
            self.cursor.execute(sql, valdict)
            self.connection.commit()
            return True
        except Exception:
            return False


    def update_value(self, table:str, selectCol:str, updateValue, searchCol:str, searchValue) -> bool: 
        """
        Queries for rows in the given table, in which the searchCol value is equal to the 
        searchValue, then updates the selectCol value with the updateValue.

        Parameters:
            table (str): table name
            selectCol (str): name of the column where the update takes place
            updateValue (Object): new value that should be stored
            searchCol (str): search column name
            searchValue (Object): search value

        Returns:
            successFlag (bool): True if update was successful, else False
        """
        sql = f"""UPDATE {table} 
        SET {selectCol} = %s
        WHERE {searchCol} = %s;"""
        try:
            rows_affected = self.cursor.execute(sql, (updateValue, searchValue))
            if rows_affected == 0:
                return False
            self.connection.commit()
            return True
        except:
            return False


