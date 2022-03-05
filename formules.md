<!-- ## PV surplus control: Heat pump

$\displaystyle SC = \int_{t_1}^{t_2} P_{HP}(t)dt - \int_{t_1}^{t_2} P_{PV}(t)dt$

Approached by control strategy: $\displaystyle A = \sum_{i=1}^{N} P_{HP}(t)\Delta t$ with $N= \frac{t_2-t_1}{\Delta t}$ where $\Delta t = C^t $ is defined in the control strategy.

## Calculations for peak demand energy optimalisation with battery storage

The period in which PV power is available (from $t_1$ to $t_2$), with the use of forecasted PV power generation and load profiles. During this period, the available energy for battery charging is calculated by (1). If there is no excess PV power in a certain time period, the effective battery charging capability is zero. So, the binary variable $z$ was used to take this effect into account:
$\displaystyle E_{excess} = \sum_{t_1}^{t_2} (P_{load,t}-P_{solar,t})z\Delta t$ (1) met $z$ gedefinieerd als: 
$ \displaystyle
z = \left\{
    \begin{array}{ll}
        1, & if(P_{solar,t}-P_{load,t}>0) \\
        0, & otherwise
    \end{array}
\right.
$
The percentage energy required to supply the load ($E$) during the peak hour period (from $t_3$ to $t_4$), is calculated by (3).
In order to supply the energy calculated in (1) the battery should at least be charged from $\Tau$ defined in (4).

$\displaystyle E = \sum_{t_3}^{t_4}(P_{solar,t}-P_{load,t})\Delta t \cdot\frac{1}{C-rate}\cdot\frac{100}{E_{bat,full}}$ (3)

$\displaystyle \sum_{\Tau}^{t_2}(P_{solar,t}-P_{load,t})z\Delta t \cdot{C-rate}\cdot\frac{100}{E_{bat,full}} > E $ (4) met $\forall\Tau\in[t_1, t_2]$

Comparison of Optimization- and Rule-Based EMS for Domestic PV-Battery Installation with Time-Varying Local SoC Limits.pdf -->

## Dynamic peak shaving limit determination using specific time window average

$\displaystyle P_{g,target}=\frac{\sum_{t=0}^{n}(X_t)+(N-(n-1))P_{g,limit}}{N}$ with $P_{g,limit}$ (Peak shaving limit), $X$ = Load demand, $N$ = time window for peak shaving optimalisation and $n$ = number of steps from start of the time window. $P_{g,target}$ is the target value of the average consumption during every time window. This formula is used to calculate the $P_{g,limit}$ every timestep.

## Calculations Arbitrage control

- $E_b$ represents the energy present in the battery in kWh;
- item $E_{battery,max}$ represents the maximum storable energy of the battery in kWh;
- item $SOC$ represents the percentage of energy remaining in the battery.

For all indications of energy SOC is used: amount of energy needed, minimum and maximum limits, and generally the capacity of the battery. SOC provides a more meaningful representation of the available battery capacity than $E_b$.

$\displaystyle E_b = E_b + (P_{batterychg} \cdot \frac{N}{n})$ where $N$ = time window and $n$ = number of steps in the window.

$\displaystyle SOC = \frac{E_b}{E_{bmax} } \cdot 100$ with $E_{bmax} = E_{battery,max} \cdot \frac{SOC}{100} $