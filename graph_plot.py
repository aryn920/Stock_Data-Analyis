import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
from mplfinance.original_flavor import candlestick_ohlc
import math
import pandas as pd
import datetime

# plotting all the data extracted in line charts and candles stick charts
fig = plt.figure(figsize=(6, 6))
fig.patch.set_facecolor('#121416')
gs = fig.add_gridspec(ncols=6, nrows=6)
ax1 = fig.add_subplot(gs[0:4, 0:4])
ax2 = fig.add_subplot(gs[0, 4:6])
ax3 = fig.add_subplot(gs[1, 4:6])
ax4 = fig.add_subplot(gs[2, 4:6])
ax5 = fig.add_subplot(gs[3, 4:6])
ax6 = fig.add_subplot(gs[4, 4:6])
ax7 = fig.add_subplot(gs[5, 4:6])
ax8 = fig.add_subplot(gs[4, 0:4])
ax9 = fig.add_subplot(gs[5, 0:4])

Stock = ['BRK-B', 'GOOG', 'AAPL', 'PYPL', 'AMZN', 'FB', 'MSFT']
plt.show()


def figure_design(ax):
    ax.set_facecolor('#091217')
    ax.tick_params(axis='both', labelsize=14, colors='white')
    ax.ticklabel_format(useOffset=False)
    ax.spines['bottom'].set_color('#808080')
    ax.spines['top'].set_color('#808080')
    ax.spines['left'].set_color('#808080')
    ax.spines['right'].set_color('#808080')


# support function to create figure designs for the graph
def subplot_plot(ax, stock_code, data, latest_price, latest_changes, target):
    ax.clear()
    ax.plot(list(range(1, len(data['close']) + 1)).data['close'], color='white', linewidth=2)

    ymin = data['close'].min()
    ymax = data['close'].max()
    ystd = data['close'].std()

    # checks if the y coordinate is 0 or not
    if not math.isnan(ymax) and ymax != 0:
        ax.set_ylim([ymin - ystd * 0.5, ymax + ystd * 3])

    ax.text(0.02, 0.95, stock_code, transform=ax.transAxes, color='#FFBF00', fontsize=11, fontweight='bold',
            horizontalalignment='left', verticalalignment='top')

    ax.text(0.2, 0.95, latest_price, transform=ax.transAxes, color='white', fontsize=11, fontweight='bold',
            horizontalalignment='left', verticalalignment='top')

    # color set to change with respect to the latest price change of the stock
    if latest_changes[0] == '+':
        colorcode = '#18b800'
    else:
        colorcode = 'ff3503'

    ax.text(0.4, 0.95, latest_changes, transform=ax.transAxes, color=colorcode, fontsize=11, fontweight='bold',
            horizontalalignment='left', verticalalignment='top')

    ax.text(0.98, 0.75, target, transform=ax.transAxes, color='#08a0e9', fontsize=11, fontweight='bold',
            horizontalalignment='left', verticalalignment='top')

    figure_design(ax)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)


# removes white the commas from the dataframe and converts the column to float data type
def string_to_number(df, column):
    if isinstance(df.iloc[0, df.columns.get_loc(column)], str):
        df[column] = df[column].str.replace(',', '')
        df[column] = df[column].astype(float)
    return df


# open high-low close function d
def read_data_ohlc(filename, stock_code, usecols):
    df = pd.read_csv(filename, header=None, usecols=usecols,
                     names=['time', stock_code, 'change', 'volume', 'target', 'pe_ratio'], index_col='time',
                     parse_dates=['time'])
    index_with_nan = df.index[df.isnull().any(axis=1)]
    df.drop(index_with_nan, 0, inplace=True)

    df.index = pd.DatetimeIndex(df.index)
    df.index = pd.DatetimeIndex(df, stock_code)
    df.index = pd.DatetimeIndex(df, 'volume')
    df.index = pd.DatetimeIndex(df, 'target')

    latest_info = df.iloc[-1, :]
    latest_price = str(latest_info.iloc[0])
    latest_changes = str(latest_info.iloc[1])

    df_vol = df['Volume'].resample('1Min').mean()
    data = df[stock_code].resample('1Min').ohlc()
    data['time'] = data.index
    data['time'] = pd.to_datetime(data['time'], format='%Y-%m-%d %H:%M:%S')
    data['MA5'] = data['close'].rolling(5).mean()
    data['MA10'] = data['close'].rolling(10).mean()
    data['MA20'] = data['close'].rolling(20).mean()

    data['volume_diff'] = df_vol.diff()
    data[data['volume_diff'] < 0] = None

    index_with_nan = data.index[data.isnull().any(axis=1)]
    data.drop(index_with_nan, 0, inplace=True)
    data.reset_index(drop=True, inplace=True)
    print(data)

    return data, latest_price, latest_changes, df['change'][-1], df['target'][-1]


def animate(i):
    # time_stamp = datetime.datetime.now()
    # time_stamp = time_stamp.strftime('%Y-%m-%d')
    # filename = str (time_stamp) + 'stock data.csv'
    filename = '2024-07-25 stock data.csv'
    data, latest_price, latest_changes, change, target = read_data_ohlc(filename, Stock[0], [1, 2, 3, 4, 5])

    candle_counter = range(len(data['open']) - 1)
    ohlc = []
    for candle in candle_counter:
        append_me = candle_counter[candle], data['open'][candle], \
            data['high'][candle], data['low'][candle], \
            data['close'][candle],
        ohlc.append(append_me)

    ax1.clear()
    candlestick_ohlc(ax1, ohlc, width=0.4, colorup='#18b800', colordown='#ff3503')
    ax1.plot(data['MA5'], color='pink', linestyle='-', linewidth=1, label='5 Minute SMA')
    ax1.plot(data['MA10'], color='orange', linestyle='-', linewidth=1, label='10 Minute SMA')
    ax1.plot(data['MA20'], color='#08a0e9', linestyle='-', linewidth=1, label='20 Minute SMA')

    leg = ax1.legend(loc='upper left', facecolor='#121416', fontsize=10)
    for text in leg.get_texts():
        plt.setp(text, color='white')
    figure_design(ax1)

    ax1.text(0.005, 1.05, Stock[0], transform=ax1.transAxes, color='black', fontsize=18, fontweight='bold',
             horizontalalignment='left', verticalalignment='center', bbox=dict(facecolor='#FFBF00'))

    ax1.text(0.2, 1.05, latest_price, transform=ax1.transAxes, color='white', fontsize=18, fontweight='bold',
             horizontalalignment='center', verticalalignment='center')
    if latest_changes[0] == '+':
        colorcode = '#18b800'
    else:
        colorcode = '#ff3503'

    ax1.text(0.4, 1.05, latest_changes, transform=ax1.transAxes, color='white', fontsize=18, fontweight='bold',
             horizontalalignment='center', verticalalignment='center')

    ax1.text(0.6, 1.05, target, transform=ax1.transAxes, color='#08a0e9', fontsize=18, fontweight='bold',
             horizontalalignment='center', verticalalignment='center')

    time_stamp = datetime.datetime.now()
    time_stamp = time_stamp.strftime('%Y-%m-%d %H:%M:%S')

    ax1.text(1.4, 2.05, time_stamp, transform=ax1.transAxes, color='white', fontsize=12, fontweight='bold',
             horizontalalignment='center', verticalalignment='center')

    ax1.grid(True, color='grey', linestyle='-', linewidth=0.3, axis='both', which='major')
    ax1.set_xticklabels([])

    data_ax2, latest_price, latest_changes, change, target = read_data_ohlc(filename, Stock[1], [1, 7, 8, 9, 10])

    subplot_plot(ax2, Stock[1], data_ax2, latest_price, latest_changes, target)

    data_ax3, latest_price, latest_changes, change, target = read_data_ohlc(filename, Stock[1], [1, 11, 12, 13, 14])
    subplot_plot(ax3, Stock[2], data_ax3, latest_price, latest_changes, target)

    data_ax4, latest_price, latest_changes, change, target = read_data_ohlc(filename, Stock[1], [1, 15, 16, 17, 18])
    subplot_plot(ax4, Stock[3], data_ax4, latest_price, latest_changes, target)

    data_ax5, latest_price, latest_changes, change, target = read_data_ohlc(filename, Stock[1], [1, 19, 20, 21, 22])
    subplot_plot(ax5, Stock[4], data_ax5, latest_price, latest_changes, target)

    data_ax6, latest_price, latest_changes, change, target = read_data_ohlc(filename, Stock[1], [1, 23, 24, 25, 26])
    subplot_plot(ax6, Stock[5], data_ax6, latest_price, latest_changes, target)

    data_ax7, latest_price, latest_changes, change, target = read_data_ohlc(filename, Stock[1], [1, 27, 28, 29, 30])
    subplot_plot(ax7, Stock[6], data_ax7, latest_price, latest_changes, target)

    ax8.clear()
    figure_design(ax8)
    ax8.axes.yais.set_visible(False)

    pos = data['open'] - data['close'] < 0
    neg = data['open'] - data['close'] > 0
    data['xaxis'] = list(range(1, len(data['volume_diff']) + 1))
    ax8.bar(data['xaxis'][pos], data['volume_diff'][pos], width=0.8, color='#18b800', align='center')
    ax8.bar(data['xaxis'][neg], data['volume_diff'][neg], width=0.8, color='#ff3503', align='center')

    # maximum value and standard deviation value of the y coord bar
    ymax = data['volume_diff'].max()
    ystd = data['volume_diff'].std()

    if not math.isnan(ymax):
        ax8.set_ylim([0, ymax + ystd * 3])

    ax8.text(0.01, 0.95, 'Volume: ' + '{:,}'.format(int(data['volume'])), transform=ax8.transAxes, color='white',
             fontsize='10', fontweight='bold', horizontalalignment='left', verticalalignment='top')

    ax8.grid(True, color='grey', linestyle='-', linewidth=0.3, axis='both', which='major')
    ax8.set_xticklabels([])


ani = animation.FuncAnimation(fig, animate, frames=100, save_count=100, interval=1)
plt.show()
