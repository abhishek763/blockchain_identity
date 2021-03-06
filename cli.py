import yaml
import requests
import json
import sqlite3

from User import User
from contextlib import closing
from termcolor import colored


name = "Cindy"
wallet_file = None
user = None
ssn = None

company = None
company_url = None
schema = None


while True:
	print("# " + name + "> ", end = "")
	inp = input()
	# print("You entered "+inp)
	inp_list = inp.split(' ')

	if inp_list[0] in ['initialize', 'init']:
		if inp_list[1] in ['user']:
			print("Enter your name: ", end = "")
			name = input()
			if name == "":
				name = "Alice Garcia"
			print("Hello "+colored(name, 'blue'))
			print("Please give your wallet file path: ", end = "")
			wallet_file = input()
			if wallet_file == "":
				wallet_file = "wallet.yaml"
			print("Enter your ssn: ", end = "")
			ssn = int(input())
			print("Your SSN:" + colored(ssn, 'blue'))
			try:
				user = User(name = name, wallet_file = wallet_file, ssn = ssn)
				print("Wallet Loaded")

			except Exception as e:
				print("Error in loading wallet")
				raise e

	if inp_list[0] in ['display', 'show', 'view']:
		if inp_list[1] in ['wallet']:
			if user.wallet == None:
				print('No wallet initialized, use "initialize user"')
				continue
			print("Certificates available: " + str(user.wallet.keys()))
			for cert_name in user.wallet.keys():
				print ("*********" + colored('CERTIFICATE', 'red') + ": "+ colored("{}".format(cert_name), 'yellow')+" ***********\n")
				cert_file = user.wallet[cert_name]
				cert = yaml.load(open(cert_file))
				for attr in cert.keys():
					if attr != 'Attributes':
						print(colored(attr, 'blue') + " : " + colored(str(cert[attr]), 'green'))
					else:
						for ind_attr in cert[attr]:
							print('\t'+colored(ind_attr, 'blue')+' : '+ colored(str(cert[attr][ind_attr]), 'green'))
				print("\n*************************************************\n")
		if inp_list[1] in ['certificate', 'cert']:
			print("Certificates available: " + str(user.wallet.keys()))
			print("Which one do you want to view? : ", end = "")
			cert_name = input()
			print ("*********" + colored('CERTIFICATE', 'red') + ": "+ colored("{}".format(cert_name), 'yellow')+" ***********\n")
			cert_file = user.wallet[cert_name]
			cert = yaml.load(open(cert_file))
			for attr in cert.keys():
				if attr != 'Attributes':
					print(colored(attr, 'blue') + " : " + colored(str(cert[attr]), 'green'))
				else:
					for ind_attr in cert[attr]:
						print('\t'+colored(ind_attr, 'blue') +' : '+ colored(str(cert[attr][ind_attr])), 'green')
			print("\n*************************************************\n")


	if inp_list[0] in ['set']:
		if inp_list[1] in ['issuer']:
			print("Enter the issuer from which you want a certificate: ")
			company = input()
			if company == "":
				company = "ABC University"
			with closing(sqlite3.connect('GlobalVs.db')) as con, con, closing(con.cursor()) as c:
				query = """SELECT url FROM GlobalVs WHERE InstituteName = '{}';""".format(company)
				c.execute(query)
				result = c.fetchall()
				company_url = result[0][0]
			# company_url = globalVs['url'][company]
			schema = requests.get(company_url+'cert_schema').json()
			print("Issuer set as "+ colored(company, 'blue') +" with url " + colored(company_url, 'blue') + " and following schema: ")
			print(schema)



	if inp_list[0] in ['get']:
		if inp_list[1] in ['certificate', 'cert']:
			if len(inp_list) == 2:
				values = {}
				if schema['Proof_Request']:
					for attr in schema['Proof_Request']:
						print("Enter "+ colored(str(attr), 'red') + " value: ", end = "")
						values[attr] = input()
				user.requestCertificate(issuer = company, values = values)
				print("Obtained certificate, stored in wallet.")

			if len(inp_list) > 2 and inp_list[2] in ['name']:
				print("Certificate name: "+colored(str(requests.get(company_url+'cert_name').json()['cert_name']), 'blue'))
			if len(inp_list) > 2 and inp_list[2] in ['public_key', 'pkey']:
				print("Public key for Issuer: "+colored(str(requests.get(company_url+'pkey').json()['pkey']), 'blue'))



