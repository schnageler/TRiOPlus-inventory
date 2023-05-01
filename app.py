import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    # Check if files were uploaded
    if 'file1' not in request.files or 'file2' not in request.files:
        return redirect(url_for('index'))

    # Get uploaded files
    file1 = request.files['file1']
    file2 = request.files['file2']

    # Check if files are valid
    if not allowed_file(file1.filename) or not allowed_file(file2.filename):
        return redirect(url_for('index'))

    # Save files to disk
    filename1 = secure_filename(file1.filename)
    filename2 = secure_filename(file2.filename)
    file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))

    # Load Excel files into Pandas dataframes
    df1 = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    df2 = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename2))

    # Get apartment counts for yesterday and today
    count_yesterday = len(df1)
    count_today = len(df2)

    # Get new properties on today's list
    new_properties = df2[~df2['Unit ID'].isin(df1['Unit ID'])][['Property', 'unit']]
    new_properties = new_properties.apply(lambda x: ' - '.join(x.astype(str)), axis=1)

    # Get removed properties from yesterday's list
    removed_properties = df1[~df1['Unit ID'].isin(df2['Unit ID'])][['Property', 'unit']]
    removed_properties = removed_properties.apply(lambda x: ' - '.join(x.astype(str)), axis=1)

    # Render results template
    return render_template('results.html',
                           count_yesterday=count_yesterday,
                           count_today=count_today,
                           new_properties=new_properties.to_list(),
                           removed_properties=removed_properties.to_list())

if __name__ == '__main__':
    app.run(debug=True)
