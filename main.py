import os, re
import argparse
import configparser
import pandas as pd
from flask import Flask, render_template, request
import time
import sqlstatements

# sqlstatements.test()

# sqlstatements.hours_report(('2024-10-10', '2024-10-27'))

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