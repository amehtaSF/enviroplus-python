from flask import Flask, send_file, request
from visualize_data import plot_var, do_plot
app = Flask(__name__)

variable_units = [
    ("temperature", "C"),
    ("pressure", "hPa"),
    ("humidity", "%"),
    ("light", "Lux"),
    ("oxidised", "kO"),
    ("reduced", "kO"),
    ("nh3", "kO"),
    ("pm1", "ug/m3"),
    ("pm25", "ug/m3"),
    ("pm10", "ug/m3")
]
units = {k: v for k, v in variable_units}

def print_urls():
    output = []
    for var, unit in variable_units:
        output.append(f'<a href=/plot?var={var}&unit={unit}')
    return '\n'.join(output)

@app.route('/')
def index():
    return print_urls()


@app.route('/plot', methods=['GET'])
def plot():

    bytes_obj = do_plot(request.args['var'], request.args['unit'])

    return send_file(bytes_obj,
                     attachment_filename='plot.png',
                     mimetype='image/png')

if __name__ == '__main__':
    app.run()