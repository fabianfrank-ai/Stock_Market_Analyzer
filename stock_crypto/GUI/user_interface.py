# Plan is to create the streamlit GUI here for tidiness
# Don't want to clutter up main.py with UI code


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import plotly.io as pio

from core.market_screener import heatmap, heatmap_portfolio, correlations
from GUI.colour_coding import color_code, verdict_color, rsi_color, ema_color, macd_color, sma_color, bollinger_color, atr_color
from core.network_graphing import plot_network
from data.fetch_data import fetch_stock_data  # for errorhandling purposes


def tab_init():
    '''Initializes all the tabs used for the GUI for the User to switch between views and features'''

    global tab1, tab2, tab3, tab4, tab5

    # create tabs with streamlit
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Stock Prices 📈", "Heatmap 🟩🟨🟥",
                                            "Stock Prediction 💹", "Portfolio Calculator ➕", "Networking Graph 📊"])


def header():
    '''Create a header for the entire web page and change color theme'''

    # change the style of the plot to dark mode (Hex colors used from ChatGPT, (I don't like the default dark mode by matplotlib)
    plt.rcParams.update({
        "figure.facecolor": "#2e2e2e",
        "axes.facecolor":   "#2e2e2e",
        "axes.edgecolor":   "#cccccc",
        "axes.labelcolor":  "#ffffff",
        "xtick.color":      "#dddddd",
        "ytick.color":      "#dddddd",
        "grid.color":       "#555555",
        "text.color":       "#ffffff",
        "figure.edgecolor": "#2e2e2e"
    })

    # Streamlit app layout with title and description
    st.title('Stock Price Viewer')
    st.write(
        'This app fetches and displays historical stock price data using yfinance and Streamlit.')


def sidebar():
    '''Create a sidebar with useful texts and information and some instructions'''

    # sidebar also defines some values like the indicators
    # not much code, just text here

    with st.sidebar:

        with st.sidebar.expander('About this app'):

            st.write('This app was created by Fabian Frank. It uses yfinance to fetch stock data and Streamlit for the web interface. You can view stock prices along with technical indicators like Simple Moving Averages (SMA) and Bollinger Bands.')
            st.write(
                'Feel free to explore and modify the code for your own projects!')
            st.write('DISCLAIMER: This app is for educational purposes only and should not be used for real trading decisions. Always do your own research and consult with a financial advisor before making investment decisions.')

        with st.sidebar.expander('SMA? Bollinger Bands? RSI? MACD? EMA?'):

            st.write('Simple Moving Averages (SMA) smooth out price data to identify trends. The 30-day SMA reacts faster to price changes than the 100-day SMA.')
            st.write('Bollinger Bands consist of a middle band (SMA), an upper band, and a lower band. Prices near the upper band may indicate overbought conditions, while prices near the lower band may indicate oversold conditions.')
            st.write('Relative Strength Index (RSI) measures the speed and change of price movements. An RSI above 70 indicates overbought conditions, while an RSI below 30 indicates oversold conditions.')
            st.write(
                'Exponential Moving Average (EMA) gives more weight to recent prices, making it more responsive to new information.')
            st.write('Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price.')
            st.write(
                'These indicators help traders make informed decisions about buying or selling stocks.')

        with st.sidebar.expander('Instructions'):

            st.write(
                '1. Select the stock ticker symbol (e.g., AMZN, MSFT, META) in the input box.')
            st.write('2. Use the slider to choose the period (in years) for which you want to fetch historical data. Note: indicatiors like SMA and Bollinger Bands are more visiblie with smaller periods')
            st.write(
                '3. The app will display the stock price along with the 30-day and 100-day SMAs and Bollinger Bands on the chart.')
            st.write(
                '4. You can select additional technical indicators to display on the chart from the sidebar.')
            st.write(
                '5. The verdict (Buy, Hold, Sell) is generated based on multiple technical indicators and displayed above the chart.')
            st.write(
                '6. You can also run the Signal Searcher to scan the S&P 500 for potential buy opportunities.')
            st.write('7. Click the "Show S&P 500 Heatmap" button to generate a heatmap of S&P 500 companies based on their daily gain/loss percentage.')

        with st.sidebar.expander('What are Stock Tickers and where can I find them ?'):

            st.write('You can find stock ticker symbols on financial websites like Yahoo Finance, Google Finance, or your brokerage platform. Common examples include AAPL for Apple, MSFT for Microsoft, and AMZN for Amazon.')

        with st.sidebar.expander('How does the verdict work?'):

            st.write(
                'The new verdict system still uses the five main indicators: SMA, Bollinger Bands, RSI, EMA and MACD.')
            st.write('However, the strength of the signals has been increased. Now, if an indicator shows a very strong buy/sell signal (e.g., RSI > 80 or < 20), it counts as 3 buy/sell signals instead of just 1. This way, the verdict is more responsive to significant market movements.')
            st.write('If 9 or more buy/sell signals are generated, the verdict will be "Strong Buy" or "Strong Sell". If 3-8 buy/sell signals are generated, the verdict will be "Buy" or "Sell". If only 1-2 buy/sell signals are generated, the verdict will be "Hold". If no buy/sell signals are generated, the verdict will also be "Hold".')
        with st.sidebar.expander('How does the prediction work?'):

            st.write(
                'The prediction uses all of the indicators of the most recent data and calculates how the price could evolve based on them')
            st.write(
                'Indicators are scaled and added together to form a weight which will be applied to the data')
            st.write('Since stocks are not purely statistical, the prediction is very likely to fail, however, a broad understanding of future developments can be made')

        with st.sidebar.expander("What is a networking graph and what does it display?"):
            st.write(
                "A networking graph displays the correlations between price movements of the S&P 500 Stocks")
            st.write("If stocks have a high correlation (e.g. 0.8+) most of their trends allign. Meaning: they tend to react to the market in a similar way")
            st.write(
                "Typically you'll find certain industries in clusters, as banks, tech, energy or healthcare are often closely intertwined")
            st.write("If you create a networking graph you'll probably see bank and loan organisations in the center with the most connections, due to the nature of their business")

        with st.sidebar.expander('Future Improvements'):

            st.write(
                '- Add more technical indicators like Volume, Stochastic Oscillator, etc.')
            st.write('- Implement user authentication for saving preferences.')
            st.write('- Allow users to save and compare multiple stocks.')
            st.write('- Integrate real-time data updates for live stock prices.')
            st.write(
                '- Add educational resources about stock trading and technical analysis.')


def user_input():
    '''Create user interface for user to chose his own data'''
    # create sliders for user input(time range and selected stock)
    # was not sure whether to include this in user_interface but it's here now for tidiness

    with tab1:
        global tab_long, tab_short
        tab_long, tab_short = st.tabs(
            ["Long term prices", "Short term prices"])

        with tab_long:
            period = st.slider('Select Period', min_value=1, max_value=20, value=10,
                               help='Select the number of years to fetch data for (1-20 years)')
            stock = st.text_input('Select Stock ticker (AMZN, MSFT, META)',
                                  help='Select the stock symbol to fetch data for', value='AMZN')
            options = ['SMA', 'Bollinger Bands', 'EMA', 'MACD', 'RSI']
            selected_indicators = st.multiselect(
                'Select Indicators to Display', options, default=['SMA', 'Bollinger Bands', 'RSI'])

        with tab_short:
            stock_short = st.text_input('Select Stock ticker (AMZN, MSFT, META)',
                                        help='Select the stock symbol uto fetch data for', value='AMZN', key="Input box for short term analysis")
            options_pills = (["1d", "2d", "3d", "4d", "5d", "6d", '7d'])
            timeframe = st.pills(
                label="Choose the timeframe you want to see", options=options_pills, default="7d")

    with tab3:
        period_prediction = st.slider('Select Period', min_value=1, max_value=20, value=10,
                                      help=' Select the number of years to fetch data for (1-20 years)', key="Slider Tab 3")
        predicted_time_frame = st.slider('Select the timeframe you want to predict', min_value=5, max_value=120,
                                         value=60, help='Decides the length of the prediction. NOTE: Larger timeframes might be unrealistic')
        stock_prediction = st.text_input('Select Stock ticker (AMZN, MSFT, META)',
                                         help='Select the stock symbol to fetch data for', value='AMZN', key="Input tab 3")

    return period, stock, period_prediction, stock_prediction, predicted_time_frame, selected_indicators, timeframe, stock_short


def user_portfolio():
    ''' Use this to get the data from the user for the portfolio'''

    with tab4:
        col1, col2, col3 = st.columns(3)

        with col1:
            stock_buy = st.text_input("Enter Stock ticker")

        with col2:
            stock_amount = st.text_input("Enter the amount you bought")

        with col3:
            buy_in_price = st.text_input(" Enter Buy-in price")

        if stock_buy and buy_in_price and stock_amount:
            if st.button("Add"):
                # only return data if input is valid, otherwise return an error
                try:
                    float(stock_amount)
                    float(buy_in_price)
                    fetch_stock_data(stock_buy, '30d', '1d')
                    return stock_buy, buy_in_price, stock_amount
                except Exception as e:
                    st.error("Uh oh! Please check your input!")


def tab_stock_chart(stock, price_change, data, selected_indicators, data_sma_30, data_sma_100, crossover_data_sma, crossover_type_sma,
                    upper_band, lower_band, ema_12, ema_26, crossover_data_ema, crossover_type_ema, macd_line, signal_line, macd_histogram, rsi, verdict, atr):
    """Use retreived data from main to create plots for the data and create heatmap if necessary"""

    with tab_long:

        fig_long_term, (ax, ax2) = plt.subplots(
            2, 1, figsize=(16, 20), sharex=True)
        fig_long_term.tight_layout(pad=5.0)

        # name the axes and add a grid
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (USD)')
        ax.grid()
        ax2.grid()
        ax2.set_ylabel('RSI')

        # HEATMAP HAS BEEN MOVED ->tab_heatmap()

        # plot the data
        # check if the price change is positive or negative and change the background color accordingly
        if price_change > 0:

            # dark green background for positive price change
            ax.set_facecolor('#003f3f')
            ax.plot(
                data.index, data['Close'], label=f'Close Price \u25B2 {price_change}%', color='white')

        else:

            # dark red background for negative price change
            ax.set_facecolor('#3f0000')
            ax.plot(
                data.index, data['Close'], label=f'Close Price \u25BC {price_change}%', color='#ff4d4d')

        # plot the selected indicators, if any are selected
        if 'SMA' in selected_indicators:

            ax.plot(data_sma_100.index, data_sma_100,
                    label='100 Day SMA', color='#f000ff', linestyle='dashdot')
            ax.plot(data_sma_30.index, data_sma_30, label='30 Day SMA',
                    color="#ffc800", linestyle='dashdot')

            # check if user chose sma as indicator
            if crossover_data_sma is not None:

                # extract date and crossover type
                for date, ctype in zip(crossover_data_sma, crossover_type_sma):

                    # check if its golden or death cross and plot accordingly

                    if ctype == 'Golden Cross':
                        # there was some trouble with plotting the markers directly on the date, so I had to find the closest date in the data index
                        # very hacky but it works

                        closest_date = data.index.get_indexer(
                            [date], method='nearest')
                        ax.plot(data.index[closest_date][0], data.loc[data.index[closest_date][0], 'Close'],
                                marker='^', color='gold', markersize=15, zorder=5)

                    elif ctype == 'Death Cross':

                        closest_date = data.index.get_indexer(
                            [date], method='nearest')
                        ax.plot(data.index[closest_date][0], data.loc[data.index[closest_date][0], 'Close'],
                                marker='v', color='black', markersize=15, zorder=5)

        if 'Bollinger Bands' in selected_indicators:

            ax.plot(upper_band.index, upper_band,
                    label='Upper Bollinger Band', color='limegreen', linestyle='--')
            ax.plot(lower_band.index, lower_band,
                    label='Lower Bollinger Band', color='red', linestyle='--')

        if 'EMA' in selected_indicators:

            ax.plot(ema_12.index, ema_12, label='12 Day EMA',
                    color="#99f5ff", linestyle='dotted')
            ax.plot(ema_26.index, ema_26, label='26 Day EMA',
                    color='#ff00ff', linestyle='dotted')

            if crossover_data_ema is not None:

                for date, ctype in zip(crossover_data_ema, crossover_type_ema):

                    if ctype == 'Golden Cross':
                        closest_date = data.index.get_indexer(
                            [date], method='nearest')
                        ax.plot(data.index[closest_date][0], data.loc[data.index[closest_date][0], 'Close'],
                                marker='^', color='cyan', markersize=15)

                    elif ctype == 'Death Cross':

                        closest_date = data.index.get_indexer(
                            [date], method='nearest')
                        ax.plot(data.index[closest_date][0], data.loc[data.index[closest_date][0], 'Close'],
                                marker='v', color='magenta', markersize=15)

        if 'MACD' in selected_indicators:

            ax2.plot(macd_line.index, macd_line,
                     label='MACD Line', color='#00ff00')
            ax2.plot(signal_line.index, signal_line,
                     label='Signal Line', color='#ff0000')
            ax2.bar(macd_histogram.index, macd_histogram,
                    label='MACD Histogram', color="#d400ff", alpha=0.5)
            ax2.axhline(0, color='grey', linestyle='--')
            ax2.set_ylabel('MACD')

        if 'RSI' in selected_indicators:

            ax2.plot(rsi.index, rsi, label='14 Day RSI', color='#ffa500')
            ax2.axhline(70, color='red', linestyle='--')
            ax2.axhline(30, color='limegreen', linestyle='--')
            ax2.fill_between(rsi.index, rsi, 70, where=(
                rsi >= 70), color='red', alpha=0.3)
            ax2.fill_between(rsi.index, rsi, 30, where=(
                rsi <= 30), color='limegreen', alpha=0.3)
            ax2.set_ylabel('RSI')

        # add a title and legend
        ax.set_title(
            f'{stock} Stock Price between {data.index[0].date()} and {data.index[-1].date()}')
        ax.legend()
        ax2.legend()

    # Give the user feedback whether to buy,sell or hold a product
        if verdict == "Buy":
            st.success(
                f'Verdict: {verdict}. According to the indicators, it might be a good time to buy {stock}. Look at the sidebar for an explanation!')
        elif verdict == "Strong Buy":
            st.success(
                f'Verdict: {verdict}. According to the indicators, it might be a very good time to buy {stock}. Look at the sidebar for an explanation!')
        elif verdict == "Strong Sell":
            st.error(
                f'Verdict: {verdict}. According to the indicators, it might be a very good time to sell {stock}.')
        elif verdict == "Sell":
            st.error(
                f'Verdict: {verdict}. According to the indicators, it might be a good time to sell {stock}.')
        else:
            st.warning(
                f'Verdict: {verdict}. According to the indicators, it might be best to hold {stock} for now.')

        if atr is not None:

            # give user a feedback over the estimated risk of buying a stock, shown with a scaled ATR
            if atr > 70:

                st.error(
                    f'Risk (ATR): {atr:.2f}%. The stock seems highly volatile. Investing in it could be a huge rist.')

            elif atr > 40 and atr <= 70:

                st.warning(
                    f'Risk (ATR): {atr:.2f}%. The stock seems volatile. Investing in it could be a risk.')

            elif atr > 20 and atr <= 40:

                st.info(
                    f'Risk (ATR): {atr:.2f}%. The stock seems somewhat volatile. Investing in it could be a moderate risk.')

            else:
                st.success(
                    f'Risk (ATR): {atr:.2f}%. The stock seems not very volatile. Investing in it should be relatively safe.')

        st.pyplot(fig_long_term)


def tab_short_term(data, stock):
    '''Creates a tab with the most recent data plotted'''
    try:
        today_data = data['Close'].iloc[-1]
        today_data = round(today_data, 2)
        beginning_data = data['Close'].iloc[0]
        beginning_data = round(beginning_data, 2)

        # basically same thing than the long term tab but short
        with tab_short:
            st.write(f"{stock} : {today_data}$")
            fig_short_term, (ax) = plt.subplots(figsize=(16, 8))

            # name the axes and add a grid
            ax.set_xlabel('Date')
            ax.set_ylabel('Price (USD)')
            ax.grid()
            # ax.set_title(f'{stock} Stock Price between {data.index[0].date()} and {data.index[-1].date()}')

            ax.plot(
                data.index, data['Close'], label=f'Movement of {stock} in a short frame', color="#EA00FF")

            st.pyplot(fig_short_term)
    except Exception as e:
        st.error(f"Oops, something went wrong, try again: {e}")


def tab_heatmap():
    '''Create a heatmap and display it as streamlit dataframe'''
    if 'heatmap_data' not in st.session_state:
        st.session_state.heatmap_data = None

    tab_quarters = []
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            # only create heatmap if it's not been created yet....
            if st.button("Create Heatmap"):

                # create a dataframe(pandas) with the heatmap function initialized in the data folder
                with st.spinner('Generating heatmap... This may take a moment.'):
                    # input none none to not interfere with historical data
                    st.session_state.heatmap_data = heatmap(None, None)

                st.write('S&P 500 Daily Change Percentage:')

        # ... or choose from a historical option
        with col2:
            # get pre calculated files from the folder and sort them
            for file in Path("stock_crypto/data_saved/heatmap_parquet").glob("*.parquet"):

                tab_quarters.append(f'{file.stem}')

            tab_quarters.sort()
            quarter_choice = st.select_slider(
                label="Select a quarter to display the heatmap from", options=tab_quarters)

            if st.button("Go"):
                st.session_state.heatmap_data = pd.read_parquet(
                    f'stock_crypto/data_saved/heatmap_parquet/{quarter_choice}.parquet').copy()

        if st.session_state.heatmap_data is not None:
            st.dataframe(st.session_state.heatmap_data.style
                         .map(color_code, subset=['Change'])
                         .map(verdict_color, subset=['Verdict'])
                         .map(sma_color, subset=['SMA Diff'])
                         .map(rsi_color, subset=['RSI'])
                         .map(bollinger_color, subset=['Bollinger %'])
                         .map(ema_color, subset=['EMA Diff'])
                         .map(macd_color, subset=['MACD Diff'])
                         .map(atr_color, subset=['Risk']))
            heatmap_csv = st.session_state.heatmap_data.to_csv(
                index=False).encode('utf-8')
            st.download_button(label="Export Heatmap as CSV",
                               data=heatmap_csv, file_name="Heatmap.csv", mime="text/csv")
            st.info("Note: Historical data uses SMA20 and SMA50 for calculations instead of SMA30 and SMA100 to better fit the shorter timeframes")


def tab_prediction(data_pred, data, timeframe):
    '''Create a portfolio calculator for input given by the user'''

    with tab3:
        try:
            fig_prediction, ax = plt.subplots(figsize=(16, 8))

            ax.set_xlabel('Date')
            ax.set_ylabel('Price (USD)')
            ax.grid()

            ax.plot(
                data.index, data['Close'], label="Stock price in the past", color='red', zorder=5)
            ax.plot(data_pred.index, data_pred['Close'],
                    label=f"Stock price prediction for the next {timeframe} days", color="#24FF07", linestyle="--")

            # removed due to bugfixing
            # ax.plot(sk_data_x, sk_data_y, label = "Sklearn Prediction")
            ax.legend()

            # take the most recent price in the prediction to indicate a potential price in the next n days
            target_price = data_pred['Close'].iloc[-1]
            target_price = round(target_price, 2)

            st.info(
                f'The selected stock has the potential to reach {target_price} USD in the next {timeframe} days')

            st.pyplot(fig_prediction)
        except Exception as e:
            st.error("Something went wrong, did you check for correct input?")


def tab_portfolio_calculator(portfolio_df):
    """Plotting of the portfolio calculator based with the input by a user"""
    portfolio_csv = portfolio_df.to_csv(index=False).encode('utf-8')

    with tab4:
        # visualize the dataframe and heatmap of the portfolio
        st.dataframe(portfolio_df.style.map(color_code, subset=['Change%']))
        st.download_button(label="Download your portfolio as csv",
                           data=portfolio_csv, file_name="Portfolio.csv", mime="text/csv")

        heatmap_portf = heatmap_portfolio(portfolio_df)
        heatmap_portf_csv = heatmap_portf.to_csv(index=False).encode('utf-8')

        st.dataframe(heatmap_portf.style
                     .map(color_code, subset=['Change'])
                     .map(verdict_color, subset=['Verdict'])
                     .map(sma_color, subset=['SMA Diff'])
                     .map(rsi_color, subset=['RSI'])
                     .map(bollinger_color, subset=['Bollinger %'])
                     .map(ema_color, subset=['EMA Diff'])
                     .map(macd_color, subset=['MACD Diff'])
                     .map(atr_color, subset=['Risk']))

        st.download_button(label="Download your heatmap as csv", data=heatmap_portf_csv,
                           file_name='Portfolio heatmap.csv', mime="text/csv")

        st.info("Note that you can only add one stock of each kind")


def tab_network_graph():
    '''Plot the networking graph'''
    network_quarter_options = []
    fig_network = None
    # just enable session state so it doesn't have to create all the data with each refresh
    if 'df_correlation' not in st.session_state:
        st.session_state.df_correlation = None

    # display the network input and output in tab 5
    with tab5:
        tab_current_adjustable, tab_historical_data = st.tabs(
            ["Show the current network", "Show historical networks"])
        st.write("Creates a Network Graph showing correlations between market movements of S&P 500 companies in the past 6 months")

        # 2 tabs within a tab to distplay a current network and historical records of networks
        with tab_current_adjustable:
            threshold = st.slider("Threshold for the correlations", min_value=0.3, max_value=1.0, value=0.7,
                                  help="Bigger correlations usually mean companies are very connected. NOTE: Be aware that a low threshold might slow your PC!")

            # give user the choice between new data or pre calculated data
            if st.button("Create a new networking Graph"):

                with st.spinner("This will take a while...Please wait"):
                    if st.session_state.df_correlation is None:
                        st.session_state.df_correlation = correlations(
                            None, None)

                    else:
                        pass

                    fig_network = plot_network(
                        st.session_state.df_correlation, threshold)

        with tab_historical_data:
            # create an option for every entry in the folder and create a select slider, then read json file
            for file in Path("stock_crypto/data_saved/correlation_parquet").glob("*.parquet"):

                network_quarter_options.append(f'{file.stem}')

            network_quarter_options.sort()
            network_quarter_choice = st.select_slider(
                label="Select a quarter to display the network graph from", options=network_quarter_options)

            threshold = st.slider("Threshold for the correlations", min_value=0.3, max_value=1.0, value=0.7,
                                  help="Bigger correlations usually mean companies are very connected. NOTE: Be aware that a low threshold might slow your PC!", key="Network threshold slider")

            if st.button("Go", key="Network go button"):
                st.session_state.df_correlation = pd.read_parquet(
                    f'stock_crypto/data_saved/correlation_parquet/{network_quarter_choice}.parquet').copy()
                fig_network = plot_network(
                    st.session_state.df_correlation, threshold)

        if fig_network is not None:
            st.plotly_chart(fig_network)
