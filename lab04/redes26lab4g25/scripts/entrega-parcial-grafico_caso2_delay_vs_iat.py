import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    'font.size': 20,
    'axes.labelsize': 21,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
    'legend.fontsize': 20,
    'font.family': 'serif',
    'axes.labelweight': 'bold',
})

# Generar con: opp_scavetool export -f "runattr:configname =~ Caso2" -o figuras/datos/caso2.csv results/Caso2-*.sca results/Caso2-*.vec
df = pd.read_csv('figuras/datos/caso2.csv')

runatts = df[df['type'] == 'runattr']
iat_map = runatts[runatts['attrname'] == 'iterationvars'][['run', 'attrvalue']]
iat_map = iat_map.rename(columns={'attrvalue': 'iat'})

scalars = df[df['type'] == 'scalar']
scalars = scalars.merge(iat_map, on='run', how='left')

vectors = df[df['type'] == 'vector']
vectors = vectors.merge(iat_map, on='run', how='left')

delay = scalars[(scalars['name'] == 'Average delay') & (scalars['module'] == 'Network.node[5].app')]
delay['value'] = delay['value'].astype(float)
delay['iat_num'] = delay['iat'].str.replace('$iat=', '').astype(float)
delay = delay.sort_values('iat_num')

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(delay['iat_num'], delay['value'], marker='o')
ax.set_xlabel('interArrivalTime (s)')
ax.set_ylabel('Demora media (s)')
ax.grid(axis='y')
fig.tight_layout()
ax.set_xticks(delay['iat_num'])
fig.savefig('figuras/caso2_delay_vs_iat.png', dpi=300)

# Figura 2: Delay a lo largo del tiempo para cada iat
delay_vectors = vectors[(vectors['name'] == 'Delay') & (vectors['module'] == 'Network.node[5].app')]

fig2, ax2 = plt.subplots(figsize=(10, 6))
for iat in sorted(delay_vectors['iat'].unique(), key=lambda x: float(x.replace('$iat=', ''))):
    subset = delay_vectors[delay_vectors['iat'] == iat]
    for _, row in subset.iterrows():
        times = np.fromstring(row['vectime'], sep=' ')
        values = np.fromstring(row['vecvalue'], sep=' ')
        ax2.plot(times, values, label=iat.replace('$iat=', 'iat='))

ax2.set_xlabel('Tiempo (s)')
ax2.set_ylabel('Demora (s)')
ax2.set_title('Demora extremo a extremo por paquete - Caso 2')
ax2.legend()
ax2.grid(axis='y')
fig2.tight_layout()
fig2.savefig('figuras/caso2_delay_temporal.png', dpi=300)

plt.show()
