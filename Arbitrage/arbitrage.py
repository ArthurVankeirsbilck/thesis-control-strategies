import pandas as pd
import matplotlib.pyplot as plt

pv = pd.read_csv('pv_1m_denhenk.csv', delimiter=',')
df = pd.read_csv('data_1m_denhenk.csv', delimiter=',')


values = df['_value'].tolist()
pvvalues = pv['_value'].tolist()



def arbitrage(Ppv, Pl, SOC, time, Eb):
    Pbatterychgmax = 5000
    Pbatterychg = 0
    Pgridexp = 0
    SOCmax = 90
    Ebmax = 13500

    if Ppv > Pl:
        if SOC < SOCmax:
            if (Ppv-Pl) > Pbatterychgmax:
                Pbatterychg = Pbatterychgmax
                Eb = Eb + (Pbatterychg*time)
                SOC = (Eb/Ebmax)*100  
                Pgridexp = Ppv-Pbatterychg
            else:
                Pbatterychg = Ppv-Pl
                Eb = Eb + (Pbatterychg*time)
                SOC = (Eb/Ebmax)*100  
        else:
            print('Battery Full')
    else:
        print('Standby')
    


    return SOC, Pbatterychg, Pgridexp, Eb

SOC = 0
Eb = 0
Pbatterychglist = []
SOClist = []
pgridexplist = []

for pv, v in zip(pvvalues, values):
    SOC, Pbatterychg, Pgridexp, Eb = arbitrage(pv, v, SOC, 1/60, Eb)
    SOClist.append(SOC)
    Pbatterychglist.append(Pbatterychg)
    pgridexplist.append(Pgridexp)

fig, axs = plt.subplots(2, 2)
axs[0, 0].plot(values, label="Consumption [kWh]")
axs[0, 0].plot(pvvalues, label="Production [kWh]")
axs[0, 0].set_title('Input data')
axs[0, 0].legend(loc="upper left")

axs[0, 1].plot(SOClist, 'tab:orange', label="SOC [%]")
axs[0, 1].set_title('SOC')
axs[0, 1].legend(loc="upper left")

axs[1, 0].plot(Pbatterychglist, 'tab:green', label="Battery Charge [kWh]")
axs[1, 0].set_title('Battery')
axs[1, 0].legend(loc="upper left")

axs[1, 1].plot(pgridexplist, 'tab:red', label="Grid Export [kWh]")
axs[1, 1].set_title('Grid Export')
axs[1, 1].legend(loc="upper left")

plt.show()


 