import pandas as pd
import matplotlib.pyplot as plt
import io

DATA_FILE = '../data/reading_data_20201024_072314.csv'


df = pd.read_csv(DATA_FILE)


variables = [#"timestamp",
             "temperature",
             "pressure",
             "humidity",
             "light",
             "oxidised",
             "reduced",
             "nh3",
             "pm1",
             "pm25",
             "pm10"]
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

def plot_var(var, units = '', rolling_window_size=1, show=True):
    x = pd.to_datetime(df['timestamp'], unit='s')
    x = x.dt.tz_localize("GMT").dt.tz_convert('America/Los_Angeles').dt.tz_localize(None)
    y = df[var].rolling(window=rolling_window_size).mean()
    plt.plot(x,y)
    plt.gcf().autofmt_xdate()
    plt.title(f'{var} {units}')
    if show:
        plt.show()

def do_plot(var, units='', rolling_window_size=1):
    plot_var(var, units='', rolling_window_size=1, show=False)
    # here is the trick save your figure into a bytes object and you can afterwards expose it via flas
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image

if __name__ == '__main__':
    for var, unit in variable_units:
        plot_var(var, units=unit, rolling_window_size=4)