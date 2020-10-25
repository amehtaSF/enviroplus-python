from flask import Flask, send_file
from visualize_data import plot_var, do_plot
app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/plot', methods=['GET'])
def plot():
    bytes_obj = do_plot("temperature", "C")

    return send_file(bytes_obj,
                     attachment_filename='plot.png',
                     mimetype='image/png')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
