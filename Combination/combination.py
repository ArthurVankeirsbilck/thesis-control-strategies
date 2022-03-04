import pandas as pd
import matplotlib.pyplot as plt

pv = pd.read_csv('pvhenkmonth.csv', delimiter=',')
df = pd.read_csv('valueshenkmonth.csv', delimiter=',')

values = df['_value'].tolist()
pvvalues = pv['_value'].tolist()
Ebmax = 13500
def arbitrage(Ppv, Pl, SOC, time, Eb):
    global Ebmax
    Pbatterychgmax = 5000
    Pbatterychg = 0
    Pgridexp = 0
    SOCmax = 90
    Pbatterydchrg = 0
    Pgridimport = 0

    if Ppv > Pl:
        Pgridimport = 0
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
        Pgridimport = Pl-Ppv
    return SOC, Pbatterychg, Pbatterydchrg*-1, Pgridimport, Pgridexp, Eb


def Average(lst):
    return sum(lst) / len(lst)

Pglimitlist = []
Pglimitinitial = 2500

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
    global Ebmax
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

def discharge_control(Pl, time, Eb, SOC):
    Pbatterydchrgmax = 5000
    global Ebmax
    Pgridimport = 0
    SOCmin = 30
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

SOC = 90
Eb = Ebmax*(SOC/100)
SOClist = []
Pbatterydchglist = []
Phouselist = []
Pbatterylist = []
SOClist = []
Eblist = []
avgpieklist = []
verbruik = []
teller = 0
windowcounter = 0
n=0
for i, (solar, v) in enumerate(zip(pvvalues, values)):
    teller += 1
    windowcounter += 1
    print(teller)
    if windowcounter == 1440:
        n +=1
        windowcounter = 0

    if teller <= 479+(n*1440) or teller >= 1019+(n*1440):
        # SOC1, Pbatterydchrg, Phouse, Eb = discharge_control(v, 1/60, Eb, SOC)
        length = i % 15 + 1
        if (i < 15): gem_list = Phouselist[:length]
        else: gem_list = Phouselist[i-length:i]
        if v > dynamic_peak_shave_limit(gem_list):
            SOC, Eb, Pbatterydchrg, Phouse = peak_reduction(v, 1/60, SOC, Eb, gem_list)
        else:
           SOC, Pbatterydchrg, Phouse, Eb = discharge_control(v, 1/60, Eb, SOC)


        Pbatterydchglist.append(Pbatterydchrg*-1)

    else:
        SOC1, Pbatterydchrg, Pbatterychrg, Phouse, Pgridexp, Eb = arbitrage(solar, v, SOC, 1/60, Eb)
        
        length = i % 15 + 1
        if (i < 15): gem_list = Phouselist[:length]
        else: gem_list = Phouselist[i-length:i]
        
        if v > dynamic_peak_shave_limit(gem_list):
            SOC, Eb, Pbatterydchrg, Phouse = peak_reduction(v, 1/60, SOC1, Eb, gem_list)
        else:
           SOC = SOC1 
        
        Pbatterydchglist.append(Pbatterydchrg)

    Phouselist.append(Phouse)
    Eblist.append(Eb)
    SOClist.append(SOC)

n=15
lijst = [Phouselist[i:i + n] for i in range(0, len(Phouselist), n)]
avgpieklistshaved = list(map(Average, lijst))

lijst = [values[i:i + n] for i in range(0, len(values), n)]
avgpieklistnotshaved = list(map(Average, lijst))

plt.plot(Pbatterydchglist)
plt.plot(values)
plt.plot(Phouselist)
plt.show()

plt.plot(pvvalues[40000:44000])
plt.plot(SOClist[40000:44000])
plt.plot(Phouselist[40000:44000])

plt.show()

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.set_title('Combination graph')
ax1.plot(pvvalues[40000:44000], 'g-', label="Grid Import [kWh]")
ax2.plot(SOClist[40000:44000], 'b-', label="SOC [%]")
ax1.plot(Phouselist[40000:44000], 'r-', label="Grid Import [kWh]")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.show()