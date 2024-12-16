import os, re
import argparse
import configparser
import pandas as pd
from flask import Flask, render_template, request
import time
import sqlstatements

application = Flask(__name__)

@application.route("/")
def home():
    return render_template('home.html')


@application.route("/tasksstatus", methods=['GET'])
def tasksstatus():
    return render_template('resultstable.html')

@application.route("/byroom", methods=['GET', 'POST'])
def byroom():
    if request.method == 'POST':
        post_values = request.form
        sqlstatements.post_to_db(post_values)

    try:
        building = request.args['building']
        room = request.args['frontdoor']
    except:
        building = 'A'
        room = '101'
    display_this_json = sqlstatements.todo_list_room(building=building, room=room)
    # display_this_json_str = display_this_jsonify.get_data(as_text=True)
    return render_template('byroom.html', display_this=display_this_json)

@application.route("/todocurrent", methods=['GET'])
def todocurrent():
    try:
        trade = request.args['trade']
    except:
        trade=False
    display_this_json = sqlstatements.todo_list_current(specify_trade=trade)

    return render_template('todocurrent.html', display_this=display_this_json)

@application.route("/roomsbypriority", methods=['GET'])
def roomsbypriority():
    display_this_json = sqlstatements.todo_list_current()

    return render_template('roomsbypriority.html', display_this=display_this_json)

@application.route("/turnedrooms", methods=['GET'])
def turnedrooms():
    display_this_json = sqlstatements.turned_rooms()

    return render_template('turnedrooms.html', display_this=display_this_json)

@application.route("/allnotesticker", methods=['GET'])
def allnotesticker():
    display_this_json = sqlstatements.all_notes_ticker(look_back=14)

    return render_template('allnotesticker.html', display_this=display_this_json)

@application.route("/completedticker", methods=['GET'])
def completedticker():
    display_this_json = sqlstatements.completed_ticker(look_back=14)

    return render_template('completedticker.html', display_this=display_this_json)

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080)