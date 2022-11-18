import unittest
import pymysql


class TestDataBase(unittest.TestCase):

    HOST = 'noah-banking.cjcipvue9uv5.us-east-1.rds.amazonaws.com'
    USER = 'admin'
    PASSWORD = 'noahadmin'
    DATABASE = 'banking'
    TABLES = {"Transactions":("from_iban", "to_iban", "amount"), 
                  "Accounts": ("iban", "balance", "user_id"),
                  "Authorization": ("hash", "user_id", "email")}
    COLUMNTYPES = {"from_iban":"text", "to_iban":"text",
                   "iban":"text", "balance":"int",
                   "user_id": "int unsigned", "hash":"binary(60)",
                   "email":"text", "amount":"int"}


    def testReachability(self):
        # check if it is able to connect to the database
        print("\n test reachability...")
        try:
            connection = pymysql.connect(host=TestDataBase.HOST, user=TestDataBase.USER, 
                                         password=TestDataBase.PASSWORD)
            connection.close()
        except Exception:
            self.fail("Could not establish connection. Please check if the database is active.")

 
    def testDatabaseStructure(self):
        print("\n test database structure...")
        connection = None
        try:
            connection = pymysql.connect(host=TestDataBase.HOST, user=TestDataBase.USER, 
                                         password=TestDataBase.PASSWORD)
        except Exception:
            self.fail("Could not establish connection. Please check if the database is active.")
        
        cursor = connection.cursor()
        # check if database exists
        try:
            data = cursor.execute(f"USE {TestDataBase.DATABASE}")
            self.assertEqual(data, 0)
        except Exception:
            connection.close()
            self.fail(f"Cound not find the database: {TestDataBase.DATABASE}")
        
        print("\n checking existance of tables, columns and its types...")
        for key, val in TestDataBase.TABLES.items():
            try:
                # check if table exists
                data = cursor.execute(f"desc {key}")
                self.assertEqual(data, len(val))
                # check if the table contains the right columns
                columnList = list(val)
                data = cursor.fetchall()
                for col in data:
                    if col[0] in columnList:
                        columnList.remove(col[0])
                        # check if the columns have the right type
                        if not col[1] == TestDataBase.COLUMNTYPES[col[0]]:
                            connection.close()
                            self.fail(f"{col[0]} does not have the right type, expected {TestDataBase.COLUMNTYPES[col[0]]} instead of {col[1]}")
                    else:
                        connection.close()
                        self.fail(f"{col[0]} is not a defined column in {key}!")
                if columnList:
                    connection.close()
                    self.fail(f"Those columns are missing in table {key}: {columnList}")
            except Exception:
                connection.close()
                self.fail(f"The table {key} is not found!")


if __name__ == "__main__":
    unittest.main()
 
