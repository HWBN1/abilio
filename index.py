from flask import Flask, render_template, request, redirect, url_for
import os
import meilisearch
import pandas as pd
import json

app = Flask(__name__)

def import_data_from_json(file_path):
    data = pd.read_json(file_path)
    return data.to_dict(orient='records')  # Convert DataFrame to a list of dictionaries

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = os.path.splitext(file.filename)[0]
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            imported_data = import_data_from_json(file_path)

            with open('config.json') as config_file:
                config = json.load(config_file)
            meilisearch_url = config['meilisearch_url']
            meilisearch_api_key = config['meilisearch_api_key']

            client = meilisearch.Client(meilisearch_url, meilisearch_api_key)
            index = client.index(filename)  # Use filename as the index name
            res = index.update_documents(imported_data, 'ID')  # Add all records to the index
            print(res)

            return redirect(url_for('success'))
    return render_template('upload.html')

@app.route('/success')
def success():
    return 'File uploaded successfully!'

if __name__ == '__main__':
    app.run(debug=True)
