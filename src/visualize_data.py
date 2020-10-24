import pandas as pd
import matplotlib.pyplot as plt

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

def plot_var(var, units = '', rolling_window_size=1):
    x = pd.to_datetime(df['timestamp'],unit='s')
    x = x.dt.tz_localize("GMT").dt.tz_convert('America/Los_Angeles').dt.tz_localize(None)
    y = df[var].rolling(window=rolling_window_size).mean()
    plt.plot(x,y)
    # plt.xticks(x, rotation='vertical')
    plt.gcf().autofmt_xdate()
    # plt.locator_params(axis='x', nbins=6)
    plt.title(f'{var} {units}')
    plt.show()


for var in variables:
    plot_var(var, rolling_window_size=4)