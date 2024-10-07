
from objects import (
    BaseContract, StockContract, OptionContract, 
    Date, Quote, OptType)
import QuantLib as ql

# Setup the environment
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates(ql.UnitedStates.NYSE)
calculation_date = Date(year=2024, month=8, day=14).to_ql()
ql.Settings.instance().evaluationDate = calculation_date

# Initialize stock object and set quote
spot_price = 100.0
stock = StockContract(
    symbol='AAPL', exchange='NASDAQ', currency='USD')
stock.set_ql_quote(value=spot_price)

# Initialize option object and set handle to stock quote
option = OptionContract(
    stock=stock, option_type=1, strike_price=145.0, 
    exercise_date=Date(year=2025, month=7, day=16), 
    multiplier='100')
option.set_ql_handle(stock.ql_quote)

# Construct the Heston process
volatility = 0.20
dividend_rate = 0.05
risk_free_rate = 0.01

v0 = volatility*volatility
kappa = 0.1
theta = v0
sigma = 0.1
rho = -0.75

flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, risk_free_rate, day_count))
div_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, dividend_rate, day_count))
heston_process = ql.HestonProcess(flat_ts, div_ts, option.ql_handle, v0, kappa, theta, sigma, rho)

# Set the option engine
engine = ql.AnalyticHestonEngine(ql.HestonModel(heston_process), 0.01, 1000)
option.ql_option.setPricingEngine(engine)

h_price = option.ql_option.NPV()
print(f'The spot price is: {spot_price:.2f} and option price is: {h_price:.2f}')

for i in range(1, 10):
    spot_price += 10
    stock.set_ql_quote(value=spot_price)
    h_price = option.ql_option.NPV()
    print(f'The spot price is: {spot_price:.2f} and option price is: {h_price:.2f}')
