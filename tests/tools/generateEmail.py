
from english_words import english_words_lower_set
from random import choice, randint
from queryTool import DataTool

"""
    Generates unique email addresses, which are not registered in the dataBase
"""


class EmailGenerator:

    MAILENDINGS = ("@gmail.com", "@hotmail.com", "@gmx.de", "@outlook.com", "@aol.de", "@tum.de")

    @staticmethod
    def generateEmail() -> str:
        keepGenerating = True
        dataTool = DataTool()
        while keepGenerating:
            dotting = randint(0,1) == 1
            numbering = randint(0,1) == 1
            longer = randint(0,1) == 1
        
            result = choice(list(english_words_lower_set))
            if dotting:
                result += "."
                if not longer and not numbering:
                    longer = True
            if longer:
                result += choice(list(english_words_lower_set))
            if numbering:
                result += str(randint(10,10000))
            result += choice(EmailGenerator.MAILENDINGS)
            keepGenerating = dataTool.exists("Authorization", "email", result)
        dataTool.close_connection()
        return result 
            



