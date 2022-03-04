import pandas as pd
import matplotlib.pyplot as plt

pv = pd.read_csv('pvhenk.csv', delimiter=',')
df = pd.read_csv('valueshenk.csv', delimiter=',')

values = df['_value'].tolist()
pvvalues = pv['_value'].tolist()


def discharge_control(Pl, time, Eb, SOC):
    Pbatterydchrgmax = 5000
    Ebmax = 13500
    Pgridimport = 0
    SOCmin = 10
    Pbatterydchrg = 0
    if SOC > SOCmin:
        if Pl > Pbatterydchrgmax:
            Pbatterydchrg = Pbatterydchrgmax
            Pgridimport = Pl - Pbatterydchrg
            Eb = Eb - (Pbatterydchrg*time)
            SOC = (Eb/Ebmax)*100
        else:
            Pbatterydchrg = Pl
            Eb = Eb - (Pbatterydchrg*time)
            SOC = (Eb/Ebmax)*100
    else:
        print('Energy Depletion Failure')
        Pgridimport = Pl
    return SOC, Pbatterydchrg, Pgridimport, Eb

def arbitrage(Ppv, Pl, SOC, time, Eb):
    Pbatterychgmax = 5000
    Pbatterychg = 0
    Pgridexp = 0
    SOCmax = 90
    Ebmax = 13500
    Pbatterydchrg = 0
    Pgridimport = 0

    if Ppv > Pl:
        if SOC < SOCmax:
            if (Ppv-Pl) > Pbatterychgmax:
                Pbatterychg = Pbatterychgmax
                SOCnext = ((Eb + (Pbatterychg*time))/Ebmax)*100 
                if SOCnext > SOCmax:
                    print('Battery full for next step')
                else:
                    Eb = Eb + (Pbatterychg*time)
                    SOC = (Eb/Ebmax)*100  
                    Pgridexp = Ppv-Pbatterychg
            else:
                Pbatterychg = Ppv-Pl
                SOCnext = ((Eb + (Pbatterychg*time))/Ebmax)*100
                if SOCnext > SOCmax:
                    print('Battery full for next step')
                else:
                    Eb = Eb + (Pbatterychg*time)
                    SOC = (Eb/Ebmax)*100  
        else:
            print('Battery Full')
    else:
        SOC, Pbatterydchrg, Pgridimport, Eb = discharge_control(Pl, time, Eb, SOC)

    return SOC, Pbatterychg, Pbatterydchrg*-1, Pgridimport, Pgridexp, Eb

SOC = 10
Eb = 1350
Pbatterychglist = []
Pbatterydchglist = []
SOClist = []
pgridexplist = []
Pgridimplist = []

for solar, v in zip(pvvalues, values):
    SOC, Pbatterychg,Pbatterydchrg,Pgridimport, Pgridexp, Eb= arbitrage(solar, v, SOC, 1/60, Eb)
    SOClist.append(SOC)
    Pbatterychglist.append(Pbatterychg)
    pgridexplist.append(Pgridexp)
    Pbatterydchglist.append(Pbatterydchrg)
    Pgridimplist.append(Pgridimport)

fig, axs = plt.subplots(3, 2)
axs[0, 0].plot(values, label="Consumption [kWh]")
axs[0, 0].plot(pvvalues, label="Production [kWh]")
axs[0, 0].set_title('Input data')
axs[0, 0].legend(loc="upper left")

axs[0, 1].plot(SOClist, 'tab:orange', label="SOC [%]")
axs[0, 1].set_title('SOC')
axs[0, 1].legend(loc="upper left")

axs[1, 0].plot(Pbatterychglist, 'tab:green', label="Battery Charge [kWh]")
axs[1, 0].set_title('Battery Charge')
axs[1, 0].legend(loc="upper left")

axs[1, 1].plot(pgridexplist, 'tab:red', label="Grid Export [kWh]")
axs[1, 1].set_title('Grid Export')
axs[1, 1].legend(loc="upper left")

axs[2, 0].plot(Pgridimplist, 'tab:blue', label="Grid Import [kWh]")
axs[2, 0].set_title('Grid Import')
axs[2, 0].legend(loc="upper left")

axs[2, 1].plot(Pbatterydchglist, 'tab:purple', label="Battery Disharge [kWh]")
axs[2, 1].set_title('Battery Disharge ')
axs[2, 1].legend(loc="upper left")

plt.show()

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()
ax1.set_title('Combination graph')
ax1.plot(Pgridimplist, 'g-', label="Grid Import [kWh]")
ax2.plot(SOClist, 'b-', label="SOC [%]")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.show()

print(pv.iloc[480])
print(pv.iloc[1019])
print(pv.iloc[1020])
print(pv.iloc[1919])
