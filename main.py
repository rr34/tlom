import os, re
import argparse
import configparser
import pandas as pd
from flask import Flask, render_template, request
import time
import sqlstatements

def create_app():

    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template('home.html')


    @app.route("/tasksstatus", methods=['GET'])
    def tasksstatus():
        return render_template('resultstable.html')


    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=8080)