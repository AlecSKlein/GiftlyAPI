#!flask/bin/python
from flask import Flask, jsonify, request
from amazon.api import AmazonAPI
import sqlite3
import modules.giftlydb as giftlydb
import modules.formatting as formatting

AMAZON_SECRET_KEY="vB/3Wi1RAF1Y/Qx3PQi1vl71UOyXswo22S/kezG+"
AMAZON_ACCESS_KEY="AKIAJLEJV5NUW2BVBLEA"
AMAZON_ASSOC_TAG="giftly-0620"

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

@app.route('/api/user/<email>/addfriend', methods=['PUT'])
def add_user_friend(userid):
    pass

@app.route('/api/user/<email>/friends/getfriends', methods=['GET'])
def get_user_friends(userid):
    if userid:
        giftlydb.select_values(values="FRIENDID, NAME, STATE")

@app.route('/api/user/<userid>/friends/<friendid>', methods=['GET'])
def get_user_friend(userid, friendid):
    pass

if __name__ == '__main__':
	app.run(debug=True)
