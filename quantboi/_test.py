import QuantLib as ql

flag = None
def raiseFlag():
    global flag
    flag = 1

me = ql.SimpleQuote(0.0)
obs = ql.Observer(raiseFlag)
obs.registerWith(me)
me.setValue(3.14)
if not flag:
    print("Case 1: Observer was not notified of market element change")

flag = None
obs.unregisterWith(me)
me.setValue(3.14)
if not flag:
    print("Case 2: Observer was not notified of market element change")