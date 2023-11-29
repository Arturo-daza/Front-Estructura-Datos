from flask import Flask, request, render_template, send_file, redirect
from werkzeug.utils import secure_filename
import requests
import pandas as pd
import os
import json
app = Flask(__name__)


@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/download')
def download_file():
    return send_file(os.path.join(os.getcwd(), 'output.csv'), as_attachment=True)


@app.route('/buscador')
def buscador():
    return render_template("indices-invertidos.html")


@app.route('/text-list')
def text():
    response = requests.get('http://127.0.0.1:8000/api')
    lista = json.loads(response.text)["Lista para la busqueda"]
    return render_template("text-list.html", lista=lista)


@app.route('/merge-sort')
def merge_sort():
    return render_template('merge_sort.html')

@app.route('/grafo', methods=['GET', 'POST'])
def grafo():
    if request.method == 'POST':
        # Obtén los datos del formulario
        aristas = request.form['aristas']
        camino = request.form['camino']

        # Convierte los datos a la estructura adecuada (puedes agregar validaciones aquí)
        aristas = eval(aristas)
        camino = eval(camino)

        # Realiza una solicitud al endpoint de FastAPI
        endpoint_url = "http://127.0.0.1:8000/api/grafo"
        data = {
            "aristas": aristas,
            "camino": camino
        }
        response = requests.post(endpoint_url, json=data)

        # Verifica si la solicitud fue exitosa (código 200)
        if response.status_code == 200:
            # Obtén los datos de la respuesta JSON
            result = response.json()
            grafo = result["grafo"]
            bfs = result["bfs"]
            dfs = result["dfs"]

            # Renderiza la plantilla Jinja2 con los resultados
            return render_template('graph.html', grafo=grafo, bfs=bfs, dfs=dfs)
        else:
            # Maneja el caso de error (puedes personalizar esto según tus necesidades)
            return f"Error al obtener datos del endpoint. Código de estado: {response.status_code}"

    # Si es una solicitud GET, simplemente renderiza el formulario vacío
    return render_template('graph.html', grafo=None, bfs=None, dfs=None)


@app.route('/binary-tree', methods=['GET', 'POST'])
def binary_tree():
    if request.method == 'POST':
        numeros = request.form.get('numeros')
        lista_numeros = [int(numero) for numero in numeros.split(',')]

        response = requests.post(
            'http://127.0.0.1:8000/api/arbol-binario', json={'lista': lista_numeros})
        data = json.loads(response.text)
        
        return render_template('binary-tree.html', data=data)
    return render_template('binary-tree.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        filename = secure_filename(file.filename)
        print(os.getcwd())
        file.save(os.path.join(os.getcwd(), filename))

        # Abre el archivo y envíalo al otro endpoint
        with open(os.path.join(os.getcwd(), filename), 'rb') as f:
            files = {'file': f}
            response = requests.post(
                'http://127.0.0.1:8000/imputacion', files=files)
            describe_data_imputed = json.loads(
                response.text)["describe_imputed"]
            describe_data_original = json.loads(
                response.text)["describe_original"]

            response_data = json.loads(response.text)["data"]
            df = pd.DataFrame.from_dict(response_data)

            # Guardar el DataFrame como un archivo CSV
            df.to_csv(os.path.join(os.getcwd(), 'output.csv'), index=False)
        context = {
            "describe_data_imputed": describe_data_imputed,
            "describe_data_original": describe_data_original
        }
        # Elimina el archivo temporal
        os.remove(os.path.join(os.getcwd(), filename))

        # return send_file(os.path.join(os.getcwd(), 'output.csv'), as_attachment=True)
        return render_template("imputed_data.html", **context)
    else:
        return render_template('imputed_upload.html')


if __name__ == '__main__':

    app.run(debug=True)
