from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
from flask_cors import CORS
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode
import os

app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"/api/*": {"origins": ["*"]}})

UPLOAD_FOLDER = '/pdfs'  # Ensure this directory exists and is writable
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, file_path):
    # Extract directory path from file_path
    directory = os.path.dirname(file_path)

    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    # Now save the file
    file.save(file_path)

def to_dict(self):  # Custom serialization method
        return {"name": self.name, "value": self.value}

def extract_barcodes_from_pdf(pdf_path):
    # Convert PDF to a list of images
    images = convert_from_path(pdf_path)
    all_barcodes = []

    # Iterate over each image to decode barcodes
    for image in images:
        barcodes = decode(image)
        for barcode in barcodes:
            all_barcodes.append(barcode.data.decode('utf-8'))
    
    return all_barcodes

class UploadPDF(Resource):
    def post(self):
        
        if 'file' not in request.files:
            return {'message': 'No file part'}, 400
        file = request.files['file']
        if file.filename == '':
            return {'message': 'No selected file'}, 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            save_file(file, file_path)

            # Extract barcodes from saved PDF
            barcodes = extract_barcodes_from_pdf(file_path)
            
            # Optional: Remove the PDF file after processing
            # os.remove(file_path)
            return {'barcodes': barcodes}, 201
        else:
            return {'message': 'Allowed file types are pdf'}, 400

api.add_resource(UploadPDF, '/api/uploadpdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
# 154.62.108.92