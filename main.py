from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from util import BoundingUtils, path_replacer
import tensorflow as tf
import os, cv2, base64, pickle
import json

app = Flask(__name__)
bounding_box = BoundingUtils()
DIR = os.path.dirname(__file__)

app.config['UPLOAD_FOLDER'] = r"./upload"
with open("./config/setting.json", "r") as f:
    config = json.load(f)

DETECTION = tf.saved_model.load(os.path.join(DIR, path_replacer(config["model"]["detection"])))
GENDER_ETHNICITY = tf.saved_model.load(os.path.join(DIR, path_replacer(config["model"]["gender-ethnicity"])))  # gender-ethnicity
DEBUG = config["debug"]
NUM_BOX = config["max_boxes"]
SCORES = config["scores"]
TERMS = config["terms"]
HOST = config["host"]
PORT = config["port"]

current_uploaded_file = None
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_size(size_in_bytes):
    KB = 1024
    MB = KB * KB
    GB = MB * KB

    if size_in_bytes < KB:
        size = size_in_bytes
        unit = 'B'
    elif size_in_bytes < MB:
        size = size_in_bytes / KB
        unit = 'KB'
    elif size_in_bytes < GB:
        size = size_in_bytes / MB
        unit = 'MB'
    else:
        size = size_in_bytes / GB
        unit = 'GB'

    formatted_size = "{:.2f} {}".format(size, unit)
    return formatted_size

def result(path):
    x = bounding_box.img_to_array(path)
    image, results = bounding_box.draw_box(
        image=x,
        models={
            "detection": DETECTION,
            "gender-ethnicity": GENDER_ETHNICITY
        },
        max_boxes=NUM_BOX,
        max_scores=SCORES,
        text_show=False,
        terms=TERMS
    )

    return image, bounding_box.str_to_list(results)

@app.route("/")
def home():
    name = "Image"
    height, width = ("NULL", "NULL")
    size = 0
    format = "NULL"
    x = os.listdir("./keys")
    results = False
    bounding_box_image = None
    # if DEBUG:print("[+] Prediction Started")
    if x:
        unpickle = pickle.load(open("./keys/key.pkl", "rb"))
        decode = base64.b85decode(unpickle).decode("utf-8")
        name, format = str(decode).split(".")
        shape = cv2.imread(f"./upload/{name}.{format}").shape[:-1]
        width, height = shape[-1], shape[0]
        size = os.path.getsize(f"./upload/{name}.{format}")
        image, results = result(f"./upload/{name}.{format}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imwrite("./static/temporal/imagesbb.png", image)
        results_x, results_y = results[:2], results[2:]
        results = results_x + results_y
        bounding_box_image = url_for("static", filename=f"temporal/imagesbb.png")
    # if DEBUG:print("[+] Prediction Ended")
    return render_template("index.html", name=name, shape=f"{width}x{height}", 
                           filesize=convert_size(size), Type=format, result_items=[results] if results else [],
                           bounding_box_image=bounding_box_image)

@app.route('/', methods=['POST'])
def upload():
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) 
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_uploaded_file = filename
            # if DEBUG:print(f"[+] Saved new file: {current_uploaded_file}")
            # print(f"Saved new file: {current_uploaded_file}")
            key = base64.b85encode(current_uploaded_file.encode("utf-8"))
            pickle.dump(key, open("./keys/key.pkl", "wb"))
            return redirect("/")
        else:
            return redirect("/")
    return redirect("/")


def run(debug):
    app.run(HOST, PORT, debug=debug)