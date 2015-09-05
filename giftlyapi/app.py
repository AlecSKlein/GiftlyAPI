#!flask/bin/python
from flask import Flask, jsonify, request, abort
from amazon.api import AmazonAPI
from Crypto.Cipher import AES
import sqlite3
import json
import hashlib
import modules.giftlydb as giftlydb
import modules.formatting as formatting
import modules.encryption as encryption

#Open the config file
with open('config.json') as config_json:
    data = json.load(config_json)

#Amazon keys
AMAZON_SECRET_KEY= data['amazon']['secret_key']
AMAZON_ACCESS_KEY= data['amazon']['access_key']
AMAZON_ASSOC_TAG=  data['amazon']['assoc_tag']
#Encryption keys
AES_KEY = hashlib.sha256(data['encryption']['aes_key']).digest()
INIT_VECTOR = data['encryption']['init_vec']
AES_MODE = AES.MODE_CFB
HASH_KEY = data['encryption']['hash_key']

amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
conn = sqlite3.connect('giftly.db')
c = conn.cursor()

giftlydb._init_db(giftlydb.get_connection())

app = Flask(__name__)

@app.route('/')
def index():
	return "Index"

@app.route('/api/user/registeruser', methods = ['POST'])
def register_user_():
    email = request.json.get('email')
    password = request.json.get('password')
    fname = request.json.get('fname')
    lname = request.json.get('lname')

    #Missing arguments
    if not email or not password or not fname or not lname:
        return abort(400)
    fname = formatting.stringify_sql(fname)
    lname = formatting.stringify_sql(lname)
    email = formatting.stringify_sql(email)

    if giftlydb.insert_user((giftlydb.generate_uuid(), email, fname, lname, formatting.stringify_sql(encryption.hash_password(password)), '1')):
        return jsonify({'email':email, 'response':200})
    else:
        return abort(400)

@app.route('/api/user/loginuser', methods = ['GET'])
def login_user():
    email = request.json.get('email')
    password = request.json.get('password')
    hashed_password = giftlydb.select_values("PASSWORD", "USER", "EMAIL=" + formatting.stringify_sql(email))[0]['PASSWORD']

    login_auth = None
    if encryption.check_hashed_password(password, hashed_password):
        login_auth = True
    else:
        login_auth = False

    return jsonify({'authenticated':login_auth, 'response':200})

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

#DOB (date of birth) is stored in the format: MM/DD/YYYY
@app.route('/api/user/addfriend', methods=['POST'])
def add_user_friend():
    userid = request.json.get('userid')
    name = request.json.get('name')
    dob = request.json.get('dob')
    success = False
    if userid and name and dob:
        name = formatting.stringify_sql(name)
        dob = formatting.stringify_sql(dob)
        success = giftlydb.insert_friend((giftlydb.generate_uuid(), userid, name, dob, '1'))

    return jsonify({'inserted':success, 'response': 200})

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
        value = giftlydb.select_values(values="NAME, DOB, STATE", table="Friend", where=("USERID="+formatting.stringify_sql(userid) + "AND FRIENDID="+formatting.stringify_sql(friendid)))
        return json.dumps(giftlydb.row_to_dict(value))

@app.route('/api/user/getfriendid', methods=['POST'])
def get_user_friend_id():
    js = request.get_json(force=True)
    userid = js.get('userid')
    name = js.get('name')
    dob = js.get('dob')
    fids = giftlydb.get_friendid_by_name_and_dob(userid, name, dob)
    ids = []
    for i, fid in enumerate(fids):
        ids.append(fids[i]['FRIENDID'])
    return jsonify({'friendid':ids, 'numids':len(ids)+1, 'respone':200})

@app.route('/api/user/friend/addinterest', methods=['POST'])
def add_friend_interest():
    js = request.get_json(force=True)
    interestname = formatting.stringify_sql(js.get('interestname'))
    friendid = js.get('friendid')
    if giftlydb.insert_interest((interestname, friendid, '1')):
        return jsonify({'friendid':friendid, 'interestname':interestname,'response':200})
    else:
        return abort(400)

@app.route('/api/user/friend/addgift', methods=['POST'])
def add_friend_gift():
    js = request.get_json(force=True)
    asin = formatting.stringify_sql(js.get('asin'))
    friendid = formatting.stringify_sql(js.get('friendid'))
    description = formatting.stringify_sql(js.get('description'))
    if giftlydb.insert_gift((asin, friendid, description, '1')):
        return jsonify({'friendid':friendid, 'asin':asin, 'response':200})
    else:
        return abort(400)

if __name__ == '__main__':
	app.run(debug=True)
