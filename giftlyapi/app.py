#!flask/bin/python
from flask import Flask, jsonify, request
from amazon.api import AmazonAPI
import sqlite3
import json
import modules.giftlydb as giftlydb
import modules.formatting as formatting

AMAZON_SECRET_KEY=""
AMAZON_ACCESS_KEY=""
AMAZON_ASSOC_TAG=""

amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
conn = sqlite3.connect('giftly.db')
c = conn.cursor()

app = Flask(__name__)

@app.route('/')
def index():
	return "Index"

@app.route('/api/lookup/similar/', methods=['GET'])
def get_similar_items():
	items = str(request.form.get('items')).split(',') if request.form.get('items') else None
	numitems = int(request.form.get('numitems')) if request.form.get('numitems') else 10
	category = str(request.form.get('category')) if request.form.get('category') else 'All'

	products = amazon.search_n(numitems, Keywords=items, SearchIndex=category)
	product_dict = {}
	for product in products:
		product_dict[product.asin] = product.title
	return jsonify({'results': product_dict})

@app.route('/api/register/<fname>/<lname>/<email>/<password>/<cpassword>', methods=['GET'])
def register_user(fname, lname, email, password, cpassword):
    missing_fields = []
    if not fname:
        missing_fields.append("First name")
    if not lname:
        missing_fields.append("Last name")
    if not email:
        missing_fields.append("Email address")
    if not password:
        missing_fields.append("Password")
    if not cpassword:
        missing_fields.append("Confirmation password")

    if not missing_fields:
        print password
        print cpassword
        if password == cpassword:
            fname = formatting.stringify_sql(fname)
            lname = formatting.stringify_sql(lname)
            email = formatting.stringify_sql(email)
            password = formatting.stringify_sql(password)

            if giftlydb.insert_user((giftlydb.generate_uuid(), email, fname, lname, password, '1')):
                return "Success!"
            else:
                return "Failure"
        else:
            return "Passwords do not match"
    else:
        return "Missing fields: " + ', '.join(missing_fields)

@app.route('/api/user/<userid>/friends/addfriend/<name>', methods=['GET'])
def add_user_friend(userid, name):
    print name
    name = formatting.stringify_sql(name)
    if giftlydb.insert_friend((giftlydb.generate_uuid(), userid, name, '1')):
        return "Success"
    else:
        return "Failure"

@app.route('/api/user/<userid>/friends/getfriends', methods=['GET'])
def get_user_friends(userid):
    if userid:
        values = giftlydb.select_values(values="FRIENDID, NAME, STATE", table="Friend", where=("USERID="+formatting.stringify_sql(userid)))
        if values:
            return json.dumps(giftlydb.row_to_dict(values))
        else:
            return "User has no associated friends"
    else:
        return "User does not exist"

@app.route('/api/user/<userid>/friends/<friendid>', methods=['GET'])
def get_user_friend(userid, friendid):
    if userid and friendid:
        value = giftlydb.select_values(values="NAME, STATE", table="Friend", where=("USERID="+formatting.stringify_sql(userid) + "AND FRIENDID="+formatting.stringify_sql(friendid)))
        return json.dumps(giftlydb.row_to_dict(value))

if __name__ == '__main__':
	app.run(debug=True)
