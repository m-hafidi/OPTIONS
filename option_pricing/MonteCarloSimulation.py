# Third party imports
import numpy as np
from scipy.stats import norm 
import matplotlib.pyplot as plt

# Local package imports
from .base import OptionPricingModel


class MonteCarloPricing(OptionPricingModel):
    """ 
    Class implementing calculation for European option price using Monte Carlo Simulation.
    We simulate underlying asset price on expiry date using random stochastic process - Brownian motion.
    For the simulation generated prices at maturity, we calculate and sum up their payoffs, average them and discount the final value.
    That value represents option price
    """

    def __init__(self, underlying_spot_price, strike_price, days_to_maturity, risk_free_rate, sigma, number_of_simulations):
        """
        Initializes variables used in Black-Scholes formula .

        underlying_spot_price: current stock or other underlying spot price
        strike_price: strike price for option cotract
        days_to_maturity: option contract maturity/exercise date
        risk_free_rate: returns on risk-free assets (assumed to be constant until expiry date)
        sigma: volatility of the underlying asset (standard deviation of asset's log returns)
        number_of_simulations: number of potential random underlying price movements 
        """
        # Parameters for Brownian process
        self.S_0 = underlying_spot_price
        self.K = strike_price
        self.T = days_to_maturity / 365
        self.r = risk_free_rate
        self.sigma = sigma 

        # Parameters for simulation
        self.N = number_of_simulations
        self.num_of_steps = days_to_maturity
        self.dt = self.T / self.num_of_steps

    def simulate_prices(self):
        """
        Simulating price movement of underlying prices using Brownian random process.
        Saving random results.
        """
        np.random.seed(20)
        self.simulation_results = None

        # Initializing price movements for simulation: rows as time index and columns as different random price movements.
        S = np.zeros((self.num_of_steps, self.N))        
        # Starting value for all price movements is the current spot price
        S[0] = self.S_0

        for t in range(1, self.num_of_steps):
            # Random values to simulate Brownian motion (Gaussian distibution)
            Z = np.random.standard_normal(self.N)
            # Updating prices for next point in time 
            S[t] = S[t - 1] * np.exp((self.r - 0.5 * self.sigma ** 2) * self.dt + (self.sigma * np.sqrt(self.dt) * Z))

        self.simulation_results_S = S

    def _calculate_call_option_price(self): 
        """
        Call option price calculation. Calculating payoffs for simulated prices at expiry date, summing up, averiging them and discounting.   
        Call option payoff (it's exercised only if the price at expiry date is higher than a strike price): max(S_t - K, 0)
        """
        if self.simulation_results_S is None:
            return -1
        return np.exp(-self.r * self.T) * 1 / self.N * np.sum(np.maximum(self.simulation_results_S[-1] - self.K, 0))
    

    def _calculate_put_option_price(self): 
        """
        Put option price calculation. Calculating payoffs for simulated prices at expiry date, summing up, averiging them and discounting.   
        Put option payoff (it's exercised only if the price at expiry date is lower than a strike price): max(K - S_t, 0)
        """
        if self.simulation_results_S is None:
            return -1
        return np.exp(-self.r * self.T) * 1 / self.N * np.sum(np.maximum(self.K - self.simulation_results_S[-1], 0))
       

    def plot_simulation_results(self, num_of_movements, text_color="#F5F5F7",
                                grid_color="#2A2A2E", path_color="#FF385C",
                                strike_color="#A1A1A6"):
        """Plots simulated price paths. Returns a matplotlib Figure.

        Theme colors are passed in so the chart sits on the app's surface;
        defaults match the dark theme.
        """
        fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
        fig.patch.set_alpha(0.0)
        ax.set_facecolor("none")

        ax.plot(self.simulation_results_S[:, 0:num_of_movements],
                color=path_color, linewidth=0.8, alpha=0.7)
        ax.axhline(self.K, color=strike_color, linestyle="--", linewidth=1.2,
                   label="Strike price")
        ax.set_xlim([0, self.num_of_steps])
        ax.set_ylabel("Simulated price", color=text_color, fontsize=10)
        ax.set_xlabel("Days in future", color=text_color, fontsize=10)
        ax.set_title(f"{num_of_movements}/{self.N} simulated paths",
                     color=text_color, fontsize=12, fontweight="bold",
                     loc="left", pad=14)
        ax.tick_params(colors=text_color, labelsize=9)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color(grid_color)
        ax.grid(axis="y", color=grid_color, linewidth=0.8, alpha=0.6)
        leg = ax.legend(loc="best", frameon=False, fontsize=9)
        for txt in leg.get_texts():
            txt.set_color(text_color)
        fig.tight_layout()
        return fig