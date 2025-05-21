import time
import redis
from flask import Flask, render_template
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd


load_dotenv()

cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379,  password=os.getenv('REDIS_PASSWORD'))
app = Flask(__name__)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

# Titanic page
@app.route("/titanic")
def titanic():
    df = pd.read_csv("data/titanic.csv")  # adjust path if needed

    # Basic table preview
    df_html = df.head().to_html(classes='table')

    # Count survivors by gender
    gender_counts = df[df['survived'] == 1]['sex'].value_counts()

    # Prepare gender data for the chart (male first, then female)
    survival_data = [
        int(gender_counts.get('male', 0)),
        int(gender_counts.get('female', 0))
    ]

    # Render template with data
    return render_template(
        "titanic.html",
        table=df_html,
        survival_data=survival_data
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)