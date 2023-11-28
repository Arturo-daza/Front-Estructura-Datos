from flask import Flask, request,render_template, send_file, redirect
from werkzeug.utils import secure_filename
import requests
import pandas as pd
import os
import json
app = Flask(__name__)


@app.route('/download')
def download_file():
    return send_file(os.path.join(os.getcwd(), 'output.csv'), as_attachment=True)

@app.route('/buscador')
def buscador():
    return render_template("indices-invertidos.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        filename = secure_filename(file.filename)
        print(os.getcwd())
        file.save(os.path.join(os.getcwd() , filename))

        # Abre el archivo y envíalo al otro endpoint
        with open(os.path.join(os.getcwd(), filename), 'rb') as f:
            files = {'file': f}
            response = requests.post('http://127.0.0.1:8000/imputacion', files=files)
            describe_data_imputed = json.loads(response.text)["describe_imputed"]
            describe_data_original = json.loads(response.text)["describe_original"]
            
            response_data = json.loads(response.text)["data"]
            df = pd.DataFrame.from_dict(response_data)
            
            # Guardar el DataFrame como un archivo CSV
            df.to_csv(os.path.join(os.getcwd(), 'output.csv'), index=False)
        context = {
            "describe_data_imputed":describe_data_imputed, 
            "describe_data_original":describe_data_original
        }
        # Elimina el archivo temporal
        os.remove(os.path.join(os.getcwd(), filename))

        # return send_file(os.path.join(os.getcwd(), 'output.csv'), as_attachment=True)
        return render_template("imputed_data.html", **context)
    else:
        return render_template('imputed_upload.html')
    
if __name__ == '__main__':
    
    app.run(debug=True)