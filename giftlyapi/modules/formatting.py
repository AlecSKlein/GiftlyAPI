__author__ = 'Alec'

from flask import jsonify

def stringify_sql(value):
    if value[0] is not "'" and value[-1] is not "'":
        return "'" + value + "'"
    return value

def format_user_json(userid=None, email=None, lname=None, fname=None, auth=None, state=None):
    user_dict = {}
    if userid: user_dict['userid'] = userid
    if email: user_dict['email'] = email
    if lname: user_dict['lname'] = lname
    if fname: user_dict['fname'] = fname
    if auth: user_dict['authenticated'] = auth
    print user_dict
    return user_dict

def format_friend_json(friendid=None, userid=None, name=None, dob=None, state=None):
    friend_dict = {}
    if friendid: friend_dict['friendid'] = friendid
    if userid: friend_dict['userid'] = userid
    if name: friend_dict['name'] = name
    if dob: friend_dict['dob'] = dob
    print friend_dict
    return jsonify(friend_dict)

def format_interest_json(interestname=None, friendid=None, state=None):
    interest_dict = {}
    if interestname: interest_dict['interestname'] = interestname
    if friendid: interest_dict['friendid'] = friendid
    print interest_dict
    return jsonify(interest_dict)

def format_gift_json(asin=None, friendid=None, title=None, state=None):
    gift_dict = {}
    if asin: gift_dict['asin'] = asin
    if friendid: gift_dict['friendid'] = friendid
    if title: gift_dict['title'] = title
    print gift_dict
    return jsonify(gift_dict)