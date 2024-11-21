import os, re
import argparse
import configparser
import pandas as pd
from flask import Flask, render_template, request
import time
import sqlstatements

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')


@app.route("/tasksstatus", methods=['GET'])
def tasksstatus():
    return render_template('resultstable.html')

@app.route("/byroom", methods=['GET', 'POST'])
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

@app.route("/todocurrent", methods=['GET', 'POST'])
def todocurrent():
    if request.method == 'POST':
        post_values = request.form
        sqlstatements.post_to_db(post_values)

    display_this_json = sqlstatements.todo_list_current()
    # display_this_json_str = display_this_jsonify.get_data(as_text=True)
    return render_template('todocurrent.html', display_this=display_this_json)


if __name__ == '__main__':
    app.run()