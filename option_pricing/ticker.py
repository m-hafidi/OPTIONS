import datetime
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

class Ticker:
    @staticmethod
    def get_historical_data(ticker, start_date=None, end_date=None):
        try:
            if start_date is None:
                start_date = datetime.datetime.now() - datetime.timedelta(days=365)
            if end_date is None:
                end_date = datetime.datetime.now()
            
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            
            if data.empty:
                raise ValueError(f"No data returned for ticker {ticker}")
            return data
        except Exception as e:
            raise Exception(f"Error fetching data for ticker {ticker}: {str(e)}")

    @staticmethod
    def get_columns(data):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        return list(data.columns)

    @staticmethod
    def get_last_price(data, column_name):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found in the DataFrame")
        return data[column_name].iloc[-1]

    @staticmethod
    def plot_data(data, ticker, column_name, text_color="#F5F5F7",
                  grid_color="#2A2A2E", line_color="#FF385C"):
        """Returns a styled matplotlib Figure for the given price series.

        Theme colors are passed in so the chart sits on the app's surface;
        defaults match the dark theme.
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found in the DataFrame")

        fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
        fig.patch.set_alpha(0.0)
        ax.set_facecolor("none")

        ax.plot(data[column_name], color=line_color, linewidth=2.0)
        ax.fill_between(data.index, data[column_name], color=line_color, alpha=0.08)

        ax.set_ylabel(column_name, color=text_color, fontsize=10)
        ax.set_title(f"{ticker} · {column_name}", color=text_color,
                     fontsize=12, fontweight="bold", loc="left", pad=14)
        ax.tick_params(colors=text_color, labelsize=9)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color(grid_color)
        ax.grid(axis="y", color=grid_color, linewidth=0.8, alpha=0.6)
        ax.margins(x=0.01)
        fig.tight_layout()
        return fig