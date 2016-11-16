from systraceAnalysis.sysTrace import *

filename="mynewtrace2.html"
tracer=sysTrace(filename)
tracer.GetAlerts()
tracer.GetJanks()