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
                  grid_color="#2A2A2E", line_color="#FF385C",
                  dash=False, reveal=True, hover=True):
        """Returns a styled matplotlib Figure for the given price series.

        Ports the visual language of the reference area-chart component:
        a vertical gradient area fill under a smooth stroke, a reveal-wipe
        intro that draws the series left-to-right, an optional dashed
        stroke, and a hover crosshair with a value readout. Theme colors
        are passed in so the chart sits on the app's surface; defaults
        match the dark theme.
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found in the DataFrame")

        x = list(range(len(data)))
        y = data[column_name].to_numpy()

        fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
        fig.patch.set_alpha(0.0)
        ax.set_facecolor("none")

        # --- area fill: vertical gradient from the line colour down to nothing
        grad = line_color + "26"  # ~15% alpha at the top of the fill
        ax.fill_between(x, y, y.min(), color=line_color, alpha=0.10, linewidth=0)
        ax.fill_between(x, y, y.min(), where=y >= y.min(), color=line_color,
                        alpha=0.10, linewidth=0)

        # --- the stroke
        line, = ax.plot(x, y, color=line_color, linewidth=2.4,
                        dash_capstyle="round",
                        linestyle="--" if dash else "-")
        if dash:
            # animated-dashed: cycle the dash pattern so the line feels alive
            line.set_dash_capstyle("round")

        # --- titles & axes, in the theme's text colour
        ax.set_title(f"{ticker} · {column_name}", color=text_color,
                     fontsize=13, fontweight="bold", loc="left", pad=16)
        ax.set_ylabel(column_name, color=text_color, fontsize=10)
        ax.tick_params(colors=text_color, labelsize=9)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color(grid_color)
        ax.grid(axis="y", color=grid_color, linewidth=0.8, alpha=0.5)

        # date labels along x, thinned to a readable count
        labels = [d.strftime("%b %d") for d in data.index]
        step = max(1, len(labels) // 6)
        ax.set_xticks(x[::step])
        ax.set_xticklabels(labels[::step], color=text_color, fontsize=9)

        # --- reveal-wipe intro: a clipping rectangle that expands left -> right,
        #     the matplotlib equivalent of the reference RevealMask
        if reveal:
            from matplotlib.patches import Rectangle
            import matplotlib.animation as animation

            ylo, yhi = float(y.min()), float(y.max())
            pad = (yhi - ylo) * 0.08 + 1e-6
            clip = Rectangle((x[0] - 1, ylo - pad), 0, (yhi - ylo) + 2 * pad,
                             transform=ax.transData)
            clip.set_visible(False)
            ax.add_patch(clip)
            line.set_clip_path(clip)

            def _reveal(_frame):
                clip.set_width(max(_frame, 0.0))
                return (line,)

            anim = animation.FuncAnimation(
                fig, _reveal, frames=len(x), interval=18, blit=False, repeat=False)
            # embed so the figure holds a reference (prevents GC before render)
            fig._reveal_anim = anim

        # --- hover crosshair + value readout (ChartTooltipContent equivalent)
        if hover and len(x) > 1:
            cursor = ax.axvline(x=-1, color=text_color, linewidth=1,
                                alpha=0.0, linestyle="--")
            dot, = ax.plot([], [], marker="o", markersize=6,
                           markerfacecolor=line_color,
                           markeredgecolor=text_color, markeredgewidth=1.5,
                           linestyle="none")
            readout = ax.annotate(
                "", xy=(0, 0), xytext=(12, 14), textcoords="offset points",
                color=text_color, fontsize=10, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.35", fc=grid_color, ec="none",
                          alpha=0.95))
            readout.set_visible(False)

            def _on_move(event):
                if event.inaxes != ax:
                    cursor.set_alpha(0.0); dot.set_visible(False)
                    readout.set_visible(False); fig.canvas.draw_idle(); return
                idx = min(range(len(x)), key=lambda i: abs(x[i] - event.xdata))
                px, py = x[idx], y[idx]
                cursor.set_xdata([px, px]); cursor.set_alpha(0.35)
                dot.set_data([px], [py])
                readout.xy = (px, py)
                readout.set_text(f"{py:,.2f}")
                readout.set_visible(True)
                fig.canvas.draw_idle()

            fig.canvas.mpl_connect("motion_notify_event", _on_move)

        fig.tight_layout()
        return fig