
from flask import Flask
from app.routes import init_routes
import os

app = Flask(__name__,template_folder="app/templates")
app.secret_key = 'super_secret_key'

UPLOAD_FOLDER = os.path.join(os.getcwd(),'app','uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)

