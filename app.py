from flask import Flask, render_template, request, jsonify
import json
from ldap3 import Server, Connection, ALL
import pandas as pd

#Complete the details in details.txt and those will be pulled from there 
json_data = open('details.txt').read()
data = json.loads(json_data)

#setting up Ldap server 
server = Server(data['SERVER_ADDRESS'], get_info=ALL)
#ldap creds to access the users
loginID = data['LOGIN_ID']
password = data['PASSWORD']

#setting up LDAP connection
try:
    conn = Connection(server, data['FULL_DOMAIN_NAME'], f'{password}', auto_bind=True)
except Exception as e:
    print(e)
    raise e

app = Flask(__name__)

def searchUserInLdap(id,name,surname,mail):
    '''
    The function helps to find the user among the AD users based on given id or name or surname or mail,
    It will filter searches based on given inputs
    Returns a dictionary 
    '''
    try:
        if len(name)>0:
            if len(surname)>0:
                conn.search(data['SEARCH_QUERY'], f'(&(objectclass=person)(&(givenName={name})(sn={surname})))', attributes=['*'])
            else:
                conn.search(data['SEARCH_QUERY'], f'(&(objectclass=person)(givenName={name}))', attributes=['*'])
        if len(surname)>0:
            if len(name)>0:
                conn.search(data['SEARCH_QUERY'], f'(&(objectclass=person)(&(givenName={name})(sn={surname})))', attributes=['*'])        
            else:
                conn.search(data['SEARCH_QUERY'], f'(&(objectclass=person)(sn={surname}))', attributes=['*'])
        if len(id)>0:
            conn.search(data['SEARCH_QUERY'], f'(&(objectclass=person)(name={id}))', attributes=['*'])  
        if len(mail)>0:
            conn.search(data['SEARCH_QUERY'], f'(&(objectclass=person)(mail={mail}))', attributes=['*'])
    except Exception as e:
        print(e)
        raise e

    list_of_entries=[]
    finalData={}
    for entry in conn.entries:
         list_of_entries.append(entry.entry_to_json())
    finalData['data'] = list_of_entries
    return finalData

@app.route('/')
def index():
	return render_template('SearchPage.html')

@app.route('/UserSearchform', methods=['POST'])
def process():  
    if request.method == 'POST':
        data = request.get_json()
        new_d={}
        for i in data:
            new_d[str(i['id'])] = i['value']
        print(new_d)
        result = searchUserInLdap(id = new_d['wwid'],
                        name = new_d['firstName'],
                        surname = new_d['lastName'],
                        mail = new_d['mail'])
                        
    return jsonify(result)

if __name__ == '__main__':
	app.run(debug=True)