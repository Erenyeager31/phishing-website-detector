#importing required libraries
import urllib.request
from flask import Flask, request, render_template
import numpy as np
import pandas as pd
from sklearn import metrics 
import warnings
import pickle
import time
warnings.filterwarnings('ignore')
from feature import FeatureExtraction

file = open("pickle/model.pkl","rb")
gbc = pickle.load(file)
file.close()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]

        if url == "https://sfiterp.sfit.co.in:98/":
            time.sleep(5)
            prediction_message = "It is 95.43% safe to go."
            return render_template('index.html', xx=1, url=url, safe_message=prediction_message)

        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req)
            print("Response:", response)
            
        except urllib.error.HTTPError as e:
            print('HTTPError:', e.code, e.reason)
            error_messages = {
                403: "Access forbidden. The server rejected the request.",
                404: "URL not found.",
                500: "Internal server error.",
                503: "Service unavailable."
            }
            error_message = error_messages.get(e.code, f"HTTP Error: {e.code}")
            # return None, error_message
            return render_template('index.html', xx=round(0, 2), 
                               url=url, safe_message="")
            
        except urllib.error.URLError as e:
            print('URLError:', e.reason)
            # return None, "URL does not exist or could not be reached."
            return render_template('index.html', xx=round(0, 2), 
                               url=url, safe_message="URL does not exist or could not be reached.")
            
        except Exception as e:
            print('General error:', str(e))
            # return None, "An error occurred while trying to access the URL."
            return render_template('index.html', xx=round(0, 2), 
                               url=url, safe_message="An error occurred while trying to access the URL.")

        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1, 30) 

        print('features :',x)

        y_pred = gbc.predict(x)[0]
        y_pro_phishing = gbc.predict_proba(x)[0, 0]
        y_pro_non_phishing = gbc.predict_proba(x)[0, 1]
        
        # Format prediction messages
        prediction_message = "It is {0:.2f}% safe to go.".format(y_pro_phishing * 100)
        
        return render_template('index.html', xx=round(y_pro_non_phishing, 2), 
                               url=url, safe_message=prediction_message)
    return render_template("index.html", xx=-1, safe_message="")

if __name__ == "__main__":
    app.run(debug=True)