#!flask/bin/python
#The primary application for the Flask api server
#Houses the routing functionality

from flask import Flask, jsonify, request, abort, Response
from functools import wraps
from Crypto.Cipher import AES
import sqlite3
import json
import hashlib
import modules.giftlydb as giftlydb
import modules.formatting as formatting
import modules.encryption as encryption
import modules.authdb as authdb
from modules.giftly_amazon import GiftlyAmazonAPI

#Open the config file
with open('config.json') as config_json:
    data = json.load(config_json)

#Amazon keys
AMAZON_SECRET_KEY= str(data['amazon']['secret_key'])
AMAZON_ACCESS_KEY= str(data['amazon']['access_key'])
AMAZON_ASSOC_TAG=  str(data['amazon']['assoc_tag'])
#Encryption keys
AES_KEY = hashlib.sha256(data['encryption']['aes_key']).digest()
INIT_VECTOR = data['encryption']['init_vec']
AES_MODE = AES.MODE_CFB
HASH_KEY = data['encryption']['hash_key']

amazon = GiftlyAmazonAPI(AMAZON_SECRET_KEY, AMAZON_ACCESS_KEY, AMAZON_ASSOC_TAG)
conn = sqlite3.connect('giftly.db')
c = conn.cursor()

giftlydb._init_db(giftlydb.get_connection())

app = Flask(__name__)

def check_auth(email, key):
    return authdb.authenticate(email, key)

@app.route('/')
def index():
	return "Index"

#LOGIN/REGISTRATION

@app.route('/api/user/getusers', methods = ['GET'])
def test():
    values = giftlydb.select_values(values="USERID, EMAIL, FNAME, LNAME, STATE", table="User")
    if values:
        value_dict = giftlydb.row_to_dict(values)
        dicts = {}
        for dict in value_dict:
            value_dict = giftlydb.row_to_dict(values)
            userid = dict['userid']
            email = dict['email']
            lname = dict['lname']
            fname = dict['fname']
            dicts[email] = formatting.format_user_json(userid=userid, email=email, lname=lname, fname=fname)

        print "dict"
        print dicts
        return jsonify({"users":dicts})

@app.route('/api/user/registeruser', methods = ['POST'])
def register_user_():
    js = request.get_json(force=True)
    email = js.get('email')
    password = js.get('password')
    fname = js.get('fname')
    lname = js.get('lname')

    #Missing arguments
    if not email or not password or not fname or not lname:
        return abort(400)
    fname = formatting.stringify_sql(fname)
    lname = formatting.stringify_sql(lname)
    email = formatting.stringify_sql(email)

    if giftlydb.insert_user((giftlydb.generate_uuid(), email, fname, lname, formatting.stringify_sql(encryption.hash_password(password)), '1')):
        values = giftlydb.select_values(values="USERID, EMAIL, FNAME, LNAME", table="User", where="EMAIL="+email)
        value_dict = giftlydb.row_to_dict(values)
        userid = value_dict[0]['userid']
        email = value_dict[0]['email']
        lname = value_dict[0]['lname']
        fname = value_dict[0]['fname']
        return jsonify(formatting.format_user_json(userid=userid, email=email, lname=lname, fname=fname))
    else:
        return abort(400)

@app.route('/api/user/loginuser', methods = ['POST'])
def login_user():
    js = request.get_json(force=True)
    email = js.get('email')
    password = js.get('password')
    if giftlydb.row_exists("EMAIL", 'User', "EMAIL="+formatting.stringify_sql(email), state='1'):
        hashed_password = giftlydb.select_values("PASSWORD", "USER", "EMAIL=" + formatting.stringify_sql(email))[0]['PASSWORD']
    else:
        print 'abort'
        return abort(400)
    login_auth = None
    if encryption.check_hashed_password(password, hashed_password):
        login_auth = True
    else:
        login_auth = False

    values = giftlydb.select_values(values="USERID, EMAIL, FNAME, LNAME, STATE", table="User", where="EMAIL="+email)
    if values:
        value_dict = giftlydb.row_to_dict(values)
        userid = value_dict[0]['userid']
        email = value_dict[0]['email']
        fname = value_dict[0]['fname']
        lname = value_dict[0]['lname']

    return jsonify(formatting.format_user_json(userid=userid, email=email, fname=fname, lname=lname, auth=login_auth))

@app.route('/api/user/getuser', methods = ['POST'])
def get_user():
    js = request.get_json(force=True)
    email = js.get('email')
    email = formatting.stringify_sql(email)
    values = giftlydb.select_values(values="USERID, EMAIL, FNAME, LNAME, STATE", table="User", where="EMAIL="+email)
    if values:
        value_dict = giftlydb.row_to_dict(values)
        userid = value_dict[0]['userid']
        email = value_dict[0]['email']
        fname = value_dict[0]['fname']
        lname = value_dict[0]['lname']
        print email
        print userid
        return jsonify(formatting.format_user_json(userid=userid, email=email, fname=fname, lname=lname))

#LOGIN/REGISTRATION
#
#USER METHODS

#Add a friend to the user based on userid
#Takes userid, name, and dob
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

    return formatting.format_friend_json()

#OUTDATED method to get all friend details of a user based on userid
@app.route('/api/user/getallfriends', methods=['POST'])
def get_user_friends():
    js = request.get_json(force=True)
    userid = js.get('userid')
    #friendid = js.get('friendid')
    if userid:
        values = giftlydb.select_values(values="FRIENDID, USERID, NAME, DOB, STATE", table="Friend", where=("USERID="+formatting.stringify_sql(userid)))
        if values:
            return jsonify({"friends":giftlydb.row_to_dict(values)})
        else:
            return jsonify({"userid":userid, "numfriends":0, "response":200})
    else:
        return jsonify({"userid":userid, "exists":"False", "response":200})

#Get friend details based on userid and friendid
@app.route('/api/user/getfriendinfo', methods=['POST'])
def get_user_friend():
    js = request.get_json(force=True)
    userid = js.get('userid')
    friendid = js.get('friendid')
    if userid and friendid:
        value = giftlydb.select_values(values="NAME, DOB, STATE", table="Friend", where=("USERID="+userid + "AND FRIENDID="+friendid))
        return json.dumps(giftlydb.row_to_dict(value))
    else:
        return jsonify({"userid":userid, "friendid":friendid, "exists":"False", "response":200})

#Performs a logical delete on a given user
@app.route('/api/user/deleteuser', methods=['POST'])
def delete_user():
    js = request.get_json(force=True)
    userid = js.get('userid')
    giftlydb.change_row_state('User', '0', 'USERID='+userid)
    return jsonify({"userid":userid, "deleted":"True", "response":200})

@app.route('/api/user/reactivateuser', methods=['POST'])
def reactivate_user():
    js = request.get_json(force=True)
    userid = js.get('userid')
    giftlydb.change_row_state('User', '1', 'USERID='+userid)
    return jsonify({"userid":userid, "reactivated":"True", "response":200})

#USER METHODS
#
#FRIEND METHODS

#Add an interest to a friend based on friendid
@app.route('/api/user/friend/addinterest', methods=['POST'])
def add_friend_interest():
    js = request.get_json(force=True)
    interestname = formatting.stringify_sql(js.get('interestname'))
    friendid = js.get('friendid')
    if giftlydb.insert_interest((interestname, friendid, '1')):
        return jsonify({'friendid':friendid, 'interestname':interestname,'response':200})
    else:
        return abort(400)

#Performs a logical delete on a given friend
#Friend is identified uniquely by friendid, does not require userid for identification
@app.route('/api/user/friend/deletefriend', methods=['POST'])
def delete_friend():
    js = request.get_json(force=True)
    friendid = js.get('friendid')
    giftlydb.update_table(table='Friend', set='STATE=0', where="FRIENDID=" + friendid)
    return jsonify({"friendid":friendid, "deleted":"True", "response":200})

#Undoes a logical delete on a given friend
#Friend is identified uniquely by friendid, does not require userid for identification
@app.route('/api/user/friend/reactivatefriend', methods=['POST'])
def reactivate_friend():
    js = request.get_json(force=True)
    friendid = js.get('friendid')
    giftlydb.change_row_state(table='Friend', state='1', where="FRIENDID=" +friendid)
    return jsonify({"friendid":friendid, "reactivated":"True", "response":200})

@app.route('/api/user/friend/addgift', methods=['POST'])
def add_friend_gift():
    js = request.get_json(force=True)
    asin = formatting.stringify_sql(js.get('asin'))
    friendid = formatting.stringify_sql(js.get('friendid'))
    description = formatting.stringify_sql(js.get('description'))
    if giftlydb.insert_gift((asin, friendid, description, '1')):
        return jsonify({"friendid":friendid, "asin":asin, "response":200})
    else:
        return abort(400)

#FRIEND METHODS
#
#AMAZON API CALLS

@app.route('/api/lookup/similar/', methods=['GET'])
def get_similar_items():
    keywords = str(request.args.get('keywords')).split(',') if request.args.get('keywords') else None
    numitems = int(request.args.get('numitems')) if request.args.get('numitems') else 10
    category = str(request.args.get('category')) if request.args.get('category') else 'All'

    product_dict = amazon.get_similar_items(keywords, numitems=numitems, category=category)

    return jsonify({'results': product_dict})

@app.route('/api/lookup/asin/', methods=['GET'])
def get_specific_item():
    asin = str(request.args.get('asin')) if request.args.get('asin') else None
    if asin:
        product = amazon.get_item_by_asin(asin)
        return jsonify({'product': product})
    else:
        return abort(404)

@app.route('/api/lookup/asins/', methods=['GET'])
def get_specific_items():
    asins = str(request.args.get('asins')) if request.args.get('asins') else None
    if asins:
        product = amazon.get_items_by_asin(asins)
        return jsonify({'products': product})
    else:
        return abort(404)

#AMAZON API CALLS

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
