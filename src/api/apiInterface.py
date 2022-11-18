
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, abort, reqparse
import sys 
import os

sys.path.append(os.path.abspath("../business"))
from businessController import BusinessController

"""
    A RESTful API Interface which checks if the required parameters are given and then 
    delegates the task to BusinessController, and sends a corresponding response to the 
    result.
"""


app = Flask(__name__)
api = Api(app)

###########################  Creation of Account ######################

class AccountCreation(Resource):

    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument("email", type=str, help="Email not given", required=True, location="json")  
        self.reqparser.add_argument("password", type=str, help="Password not given", required=True, location="json")
        self.reqparser.add_argument("balance", type=int, help="Balance not given", required=True, location="json")
        self.businessController = BusinessController()


    def post(self):
        args = self.reqparser.parse_args()
        iban = self.businessController.createAccount(args["email"], args["password"], args["balance"])
        if iban == None:
            abort(404, message="Could not create new account")
        return jsonify({"iban":iban})

api.add_resource(AccountCreation, "/createAccount")

#######################################################################


############################ Adding an Account ########################

class AccountAddition(Resource):

    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument("email", type=str, help="Email not given", required=True, location="json")  
        self.reqparser.add_argument("password", type=str, help="Password not given", required=True, location="json")
        self.reqparser.add_argument("balance", type=int, help="Balance not given", required=True, location="json")
        self.businessController = BusinessController()


    def post(self):
        args = self.reqparser.parse_args()
        iban = self.businessController.addAccount(args["email"], args["password"], args["balance"])
        if iban == None:
            abort(404, message="Could not create new account")
        return jsonify({"iban":iban})

api.add_resource(AccountAddition, "/addAccount")

########################################################################


############################# Transfer Money ###########################

class TransferMoney(Resource):

    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument("email", type=str, help="Email not given", required=True, location="json")  
        self.reqparser.add_argument("password", type=str, help="Password not given", required=True, location="json")
        self.reqparser.add_argument("from_iban", type=str, help="IBAN not given", required=True, location="json")
        self.reqparser.add_argument("to_iban", type=str, help="IBAN not given", required=True, location="json")
        self.reqparser.add_argument("amount", type=int, help="Transfer amount not given", required=True, location="json")
        self.businessController = BusinessController()


    def put(self):
        args = self.reqparser.parse_args()
        result = self.businessController.transferMoney(args["email"], args["password"], args["from_iban"], args["to_iban"], args["amount"])
        if not result:
            abort(404, message="Could not transfer money")
        return jsonify(success=True)

api.add_resource(TransferMoney, "/transfer")

#########################################################################


############################## Retrieve Balance #########################

class RetrieveBalance(Resource):

    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument("email", type=str, help="Email not given", required=True, location="json")  
        self.reqparser.add_argument("password", type=str, help="Password not given", required=True, location="json")
        self.reqparser.add_argument("iban", type=str, help="IBAN not given", required=True, location="json")
        self.businessController = BusinessController()


    def get(self):
        args = self.reqparser.parse_args()
        result = self.businessController.retrieveBalance(args["email"], args["password"], args["iban"])
        if result is None:
            abort(404, message="Could not retrieve balance")
        return jsonify({"balance":result})

api.add_resource(RetrieveBalance, "/stats")

##########################################################################


########################## Retrieve Transfer History #####################

class RetrieveTransferHistory(Resource):

    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument("email", type=str, help="Email not given", required=True, location="json")  
        self.reqparser.add_argument("password", type=str, help="Password not given", required=True, location="json")
        self.reqparser.add_argument("iban", type=str, help="IBAN not given", required=True, location="json")
        self.businessController = BusinessController()


    def get(self):
        args = self.reqparser.parse_args()
        result = self.businessController.retrieveTransferHistory(args["email"], args["password"], args["iban"])
        if result is None:
            abort(404, message="Could not retrieve transfer history")
        return jsonify({"sent":result["sent"], "received":result["received"]})

api.add_resource(RetrieveTransferHistory, "/history")

#############################################################################


if __name__ == "__main__":
    app.run()

