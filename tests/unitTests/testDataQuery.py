
import unittest
import pymysql
from random import randint, sample, randbytes, choice, uniform
from logging import exception
import sys
import string
import os

sys.path.append(os.path.abspath("../../src/business/"))
from dataQuery import DataFetcher

"""
    Consistancy in storing and reading data from the Database is a crucial component,
    especially for project like these where sensitive information is used.
    This is why dataQuery.py is a important program and should be tested throughly.
    TestDataFetcher tests every function of dataQuery.py by generating random data 
    and tables where the DataFetcher should operate on.
"""


class TestDataFetcher(unittest.TestCase):

    HOST = 'noah-banking.cjcipvue9uv5.us-east-1.rds.amazonaws.com'
    USER = 'admin'
    PASSWORD = 'noahadmin'
   
    # test the ability of correctly fetching stored data
    def testQueryAbility(self):
        TYPESDICT = {"INT": TestDataFetcher.generateInt, "TEXT": TestDataFetcher.generateText}
        connection = pymysql.connect(host=TestDataFetcher.HOST, user=TestDataFetcher.USER,
                                     password=TestDataFetcher.PASSWORD)
        cursor = connection.cursor()
        cursor.execute("USE banking")
        self.dropTestTable(connection, cursor)

        # iterate over diffrent types 
        for types, genfunc in TYPESDICT.items():
            createdTable = False
            fetcher = DataFetcher()
            try:
                # create new table, generate and store a random value
                cursor.execute(f"CREATE TABLE TestTable (test {types}, test2 TEXT);")
                connection.commit()
                createdTable = True
                value = genfunc()
                compare_value = value
                if type(value) is str:
                    value = f"'{value}'"
                cursor.execute( f"INSERT INTO TestTable (test, test2) VALUES ({value}, 'test2');")
                connection.commit()
                print(f"Testing with type {types}: {value}, stored in TestTable/test")

                # test exists() method
                if not fetcher.exists("TestTable", "test", compare_value):
                    self.fail(f"exist() can't find the {types}: {value}") 

                # test get_rows_search() method 
                data = fetcher.get_rows_search("TestTable", "test", compare_value)
                if len(data) < 1 or data[0][0] != compare_value:
                    self.fail(f"get_rows_search() can't find the {types}: {value}") 

                # test get_val_search() method
                data = fetcher.get_val_search("TestTable", "test2", "test", compare_value)
                if len(data) < 1 or data[0][0] != "test2":
                    self.fail(f"get_rows_search() can't find the {types}: {value}")

            except:
                self.fail("Failed due to an Exception!")

            if createdTable:
                fetcher.close_connection()
                self.dropTestTable(connection, cursor)

    # test the subjects ability to store data
    def testEditability(self):
        TYPESDICT = {"INT": TestDataFetcher.generateInt, "TEXT": TestDataFetcher.generateText}
        connection = pymysql.connect(host=TestDataFetcher.HOST, user=TestDataFetcher.USER,
                                     password=TestDataFetcher.PASSWORD)
        cursor = connection.cursor()
        cursor.execute("USE banking")
        self.dropTestTable(connection, cursor)


        fetcher = DataFetcher()
        createdTable = False
        try:
            # create table with random amount of columns and random types
            columnAmount = randint(3,20)
            sql = "CREATE TABLE TestTable ("
            columnValueDict = {}
            for i in range(columnAmount):
                rand_type, genfunc = choice(list(TYPESDICT.items()))
                # generate and save the expected values 
                value = genfunc()
                columnValueDict[f"test{i}"] = value
                sql += f"test{i} {rand_type}"
                if i < columnAmount - 1:
                    sql += ", "
                else:
                    sql += ");"
            cursor.execute(sql)
            connection.commit()
            createdTable = True 
            print(f"Testing with {columnAmount} columns and its expected values: {columnValueDict}")

            # test add_row() by making it store the expected values 
            fetcher.add_row("TestTable", columnValueDict)
            connection.begin()
            cursor.execute("SELECT * FROM TestTable")
            data = cursor.fetchall()
            # validate if each expected value is at its right place 
            if len(data) == 1:
                values = list(columnValueDict.values())
                for result in data[0]:
                    expected = values.pop(0)
                    if result != expected:
                        self.fail(f"add_row(): Wrongly stored {result} instead of {expected}")
                if values:
                    self.fail("add_row(): Did not store all values!")
            else:
                self.fail("add_row(): did not store anything!")

            # test update_value() by making it change a specific value
            # NOTE This test case assumes that the previous test case succeeded
            typesGeneratorDict = {str:TestDataFetcher.generateText, int:TestDataFetcher.generateInt}
            selectCol = choice(list(columnValueDict.keys()))
            newValue = typesGeneratorDict[type(columnValueDict[selectCol])]()
            searchCol = choice(list(columnValueDict.keys()))
            searchValue = columnValueDict[searchCol]
            fetcher.update_value("TestTable", selectCol, newValue, searchCol, searchValue)
            print(f"Test: update {selectCol} to {newValue}, if {searchCol} is {searchValue}")

            # validate if the update did happen in the right place 
            columnValueDict[selectCol] = newValue
            values = list(columnValueDict.values())
            connection.begin()
            cursor.execute("SELECT * FROM TestTable")
            data = cursor.fetchall()
            if len(data) == 1:
                for result in data[0]:
                    expected = values.pop(0)
                    if result != expected:
                        self.fail(f"update_value(): {result} instead of {expected}")
                if values:
                    self.fail("update_value(): Did not store all values!")
            else:
                self.fail("update_value(): Did not find stored data")


        except Exception:
            self.fail("Failed because of an Exception!")

        if createdTable:
            fetcher.close_connection()
            self.dropTestTable(connection, cursor)

    # Executing the tests above a certain amount of times
    def testOften(self):
        TESTAMOUNT = 0
        for i in range(TESTAMOUNT):
            self.testQueryAbility()
        for j in range(TESTAMOUNT):
            self.testEditability()


    # helper methods

    def dropTestTable(self,conn, cursor):
        try:
            cursor.execute("DROP TABLE IF EXISTS TestTable")
            conn.commit()
        except Exception:
            exception("COULD NOT DELTE 'TestTable', TRY MANUALLY")

    @staticmethod
    def generateInt() -> int:
        # as sys.maxsize() would be too big for the database, here we need to 
        # adapt and use the classic limits. 
        return randint(-2147483648, 2147483647)

    # generates random alphanumeric text
    @staticmethod
    def generateText() -> str:
        n = randint(5,50)
        letters = string.ascii_letters + string.digits
        # important to use sample instead of choice, as choice often leads to duplicated letters
        return ''.join(sample(letters, n))

    #NOTE planned to test with random floats, but ran into problems as MySQL approximates when
    #     storing floats
    @staticmethod
    def generateFloat() -> float:
        return uniform(-1000000, 1000000)

    #NOTE planned to test with random bytes, but sill in construction
    @staticmethod
    def generateBytes() -> bytes:
        n = randint(5,50)
        return randbytes(n)


# execute test
if __name__ == "__main__":
    unittest.main()
