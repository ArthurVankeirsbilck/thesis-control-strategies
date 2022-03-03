# Control Strategy development

## Peak reduction:

Dynamic peak shaving limit determination using specific time window average.

Tested on a historical dataset within a timerange of 2022-02-26T00:01:00Z to 2022-02-27T00:00:00Z, data is drawn from a household in Zwevegem, Belgium. This logic will be converted into an object-oriented Golang library.

### Schematic

![Alt text](Images/Schematic_peakreduction.png)

### Dynamic peak shaving limit determination using specific time window average formula

![Alt text](Images/Formula_peakreduction.png)

### Results

![Alt text](Images/Results_peakreduction.png)

## Arbitrage

Basic control for charging and discharging a battery. Charging is done in function of the produced energy of the PV-installation. Discharging occurs as soon as $P_l$ > $P_pv$.

### Charging

![Alt text](Images/Schematic_arbitrage_charging)

### Discharging

![Alt text](Images/Schematic_arbitrage_discharging)

### Results

![Alt text](Images/Results_arbitrage)

![Alt text](Images/Results2_arbitrage)

