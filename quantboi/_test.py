import QuantLib as ql

today = ql.Date(7, ql.March, 2014)
ql.Settings.instance().evaluationDate = today

option = ql.EuropeanOption(ql.PlainVanillaPayoff(ql.Option.Call, 100.0),
ql.EuropeanExercise(ql.Date(7, ql.June, 2014)))

u = ql.SimpleQuote(100.0)
r = ql.SimpleQuote(0.01)
sigma = ql.SimpleQuote(0.20)

riskFreeCurve = ql.FlatForward(0, ql.TARGET(),
ql.QuoteHandle(r), ql.Actual360())
volatility = ql.BlackConstantVol(0, ql.TARGET(),
ql.QuoteHandle(sigma), ql.Actual360())

process = ql.BlackScholesProcess(ql.QuoteHandle(u),
ql.YieldTermStructureHandle(riskFreeCurve),
ql.BlackVolTermStructureHandle(volatility))

engine = ql.AnalyticEuropeanEngine(process)

option.setPricingEngine(engine)

print(option.NPV())