from flask import Flask, request
from flask_restful import Resource, Api 
from flask_jsonpify import jsonify
import rsa
import sys
sys.path.append('../')
from Issuer import Issuer 
import json

import sqlite3

conn = sqlite3.connect("GlobalVs.db")
c = conn.cursor()

query = """INSERT INTO GlobalVs VALUES ( '{}', '{}', '{}') ;""".format('SBI Bank', 'http://localhost:8082/', 'loan')
print(query)
try:
	c.execute(query)
	conn.commit()
except:
	print("Not inserted")


app = Flask(__name__)


database = {121001: {"first_name": "Alice", "last_name": "Garcia", "loan_amt":100000},
			121002: {"first_name": "Bob", "last_name": "Marley", "loan_amt":200000}}



sbi_bank = Issuer(name='SBI Bank', schema='schemas/loan.yaml', cert_name = 'loan', db=database)

@app.route("/")
def hello():
	with open("servers/company.html", 'r') as f:
		return f.read().format("SBI Bank", "<p>Salary : >1000</p><p>ssn : exists</p>", "8082")


@app.route("/pkey")
def get_pkey():
	return jsonify({"pkey":sbi_bank.keypair[0].save_pkcs1()})

@app.route("/cert_name")
def get_cert_name():
	return jsonify({"cert_name":"loan"})

@app.route("/cert_schema")
def get_schema():
	return jsonify(sbi_bank.schema)

@app.route("/get_cert", methods = ['POST'])
def issue():
	# dis = {'answer':str(int(request.json['a'])+int(request.json['b']))}

	# print(request.json)

	proofs = request.json['proofs']
	values = request.json['values']
	receiver = request.json['receiver']
	recv_ssn = request.json['recv_ssn']
	maker_addr = '0x9e7cd1df366a5d315e0f42d3d3e3100943281cb0'
	response = json.loads(sbi_bank.issue(proofs = proofs, values = values, receiver = receiver, maker_addr=maker_addr , recv_ssn = recv_ssn))

	return jsonify(response),201

if __name__ == '__main__':
	app.run(port=8082)