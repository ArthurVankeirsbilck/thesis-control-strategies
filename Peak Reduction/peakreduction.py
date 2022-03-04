import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
Pglimitlist = []
Pglimitinitial = 1500

def dynamic_peak_shave_limit(lijst):
    Pglimit = ((Pglimitinitial*15)-sum(lijst))/(15-(len(lijst)-1))
    if Pglimit < 0:
        Pglimit = 0
    return Pglimit

test=[]
teller = 0
def peak_reduction(Pl, time, SOC, Eb, lijst):
    global teller
    teller += 1
    Pbattery = 0
    SOCmin = 10
    Pbatterymax = 5000
    Ebmax = 13500
    test.append(dynamic_peak_shave_limit(lijst))
    if Pl > dynamic_peak_shave_limit(lijst):
        if SOC > SOCmin:
            if Pbatterymax > (Pl - dynamic_peak_shave_limit(lijst)):
                SOCnext = ((Eb - (Pbattery*time))/Ebmax)*100 
                if SOCnext < SOCmin:
                    print('SOC to low for next step.')
                else:
                    # print('Battery --> House')
                    Pbattery = Pl - dynamic_peak_shave_limit(lijst) 
                    Eb = Eb - (Pbattery*time)
                    SOC = (Eb/Ebmax)*100  
            else:
                print('Undersized inverter', teller)
        else:
            # print('Energy Depletion Failure')
            pass
    else:
        # print('BESS in standby')
        pass
    
    return SOC, Eb, Pbattery, Pl-Pbattery

df = pd.read_csv('datadata.csv', delimiter=',')
df.columns = ['_value'] #'indx', 'Time', 
values = df['_value'].tolist()

SOC = 90
Eb = 13500*(SOC/100)

Phouselist = []
Pbatterylist = []
SOClist = []
Eblist = []
avgpieklist = []
verbruik = []

def Average(lst):
    return sum(lst) / len(lst)

for i, v in enumerate(values):
    length = i % 15 + 1

    if (i < 15): gem_list = Phouselist[:length]
    else: gem_list = Phouselist[i-length:i]

    # print(gem_list)

    SOC, Eb, Pbattery, Phouse = peak_reduction(v, 1/60, SOC, Eb, gem_list)
    Phouselist.append(Phouse)
    Pbatterylist.append(Pbattery)
    SOClist.append(SOC)
    Eblist.append(Eb)
n=15
lijst = [Phouselist[i:i + n] for i in range(0, len(Phouselist), n)]
avgpieklistshaved = list(map(Average, lijst))

lijst = [values[i:i + n] for i in range(0, len(values), n)]
avgpieklistnotshaved = list(map(Average, lijst))

print(Pglimitlist[600:635])

fig, axs = plt.subplots(3, 2)
axs[0, 0].plot(Phouselist, label="Consumption [kWh]")
axs[0, 0].set_title('Consumption with Peak Reduction')
axs[0, 0].legend(loc="upper left")

axs[0, 1].plot(values, 'tab:orange', label="Consumption [kWh]")
axs[0, 1].set_title('Consumption')
axs[0, 1].legend(loc="upper left")

axs[1, 0].plot(Pbatterylist, 'tab:green', label="Battery Discharge [kWh]")
axs[1, 0].set_title('Battery')
axs[1, 0].legend(loc="upper left")

axs[1, 1].plot(SOClist, 'tab:red', label="SOC [%]")
axs[1, 1].set_title('SOC')
axs[1, 1].legend(loc="lower left")

axs[2, 0].plot(test, color = 'r', linestyle = '--', label="Grid Limit [kW]")
axs[2, 0].plot(values, alpha=0.8, label="Original Consumption [kWh]")
axs[2, 0].plot(Phouselist, alpha=0.8, label="Peak-Shaved Consumption [kWh]")
axs[2, 0].set_title('Combination Graph')
axs[2, 0].legend(loc="upper left")

axs[2, 1].plot(avgpieklistshaved, label="Quarter-average Peak-shaved [kWh]")
axs[2, 1].plot(avgpieklistnotshaved, label="Quarter-average original [kWh]")
axs[2, 1].axhline(y = Pglimitinitial, color = 'r', linestyle = '--', label="Grid Limit [kW]")
axs[2, 1].set_title('Quarter hour average')
axs[2, 1].legend(loc="upper left")
x, y, text = 102, -100, "$P_{g,limit}=$"+"{}\n".format(Pglimitinitial)+"$P_{max,wo,PS}=$"+"{}\n".format(round(max(avgpieklistnotshaved)))+"$P_{max,PS}=$"+"{}".format(round(max(avgpieklistshaved)))
axs[2, 1].text(x, y, text)
plt.show()

for v in avgpieklistshaved:
    f.write(str(v)+'\n')
# ax = plt.gca()
# plt.plot(test, color = 'r', linestyle = '--')
# plt.plot(values, alpha=0.8)
# plt.plot(Phouselist, alpha=0.8)
# plt.show()

# plt.plot(values, alpha=0.8)
# plt.plot(Phouselist, alpha=0.8)
# plt.plot(Pbatterylist)

# plt.show()

# plt.plot(avgpieklistshaved)
# plt.plot(avgpieklistnotshaved)
# plt.axhline(y = Pglimitinitial, color = 'r', linestyle = '--')
# plt.show()

f.close()
