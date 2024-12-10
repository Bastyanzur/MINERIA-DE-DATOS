import os
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones'

# Carpeta temporal para guardar archivos procesados
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verifica si el archivo está en la solicitud
        if 'file' not in request.files:
            return "No se seleccionó ningún archivo."
        
        file = request.files['file']
        
        # Verifica si el archivo tiene contenido
        if file.filename == '':
            return "No se seleccionó ningún archivo válido."
        
        if file:
            # Guarda el archivo en la carpeta temporal
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Procesa el archivo y redirige al dashboard
            return redirect(url_for('dashboard', filename=file.filename))
    
    return render_template('index.html')


@app.route('/dashboard/<filename>')
def dashboard(filename):
    # Carga el archivo procesado
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        # Lee el archivo CSV
        df = pd.read_csv(filepath)
    except Exception as e:
        return f"Error leyendo el archivo: {e}"
    
    # Detecta vulnerabilidades
    vulnerabilities = detect_vulnerabilities(df)
    
    # Genera estadísticas básicas
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'null_values': df.isnull().sum().sum(),
        'duplicate_rows': df.duplicated().sum()
    }
    
    return render_template(
        'dashboard.html',
        tables=df.to_html(classes='table table-striped'),
        vulnerabilities=vulnerabilities,
        stats=stats
    )


def detect_vulnerabilities(df):
    """
    Detecta vulnerabilidades básicas en un archivo CSV.
    """
    vulnerabilities = []
    
    # Verificar valores nulos
    if df.isnull().values.any():
        vulnerabilities.append("El archivo contiene valores nulos.")
    
    # Verificar duplicados
    if df.duplicated().any():
        vulnerabilities.append("El archivo contiene filas duplicadas.")
    
    if not vulnerabilities:
        vulnerabilities.append("No se encontraron vulnerabilidades.")
    
    return vulnerabilities


if __name__ == '__main__':
    app.run(debug=True)