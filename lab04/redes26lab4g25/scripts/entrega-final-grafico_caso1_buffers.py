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

# Generar con: opp_scavetool export -f "runattr:configname =~ Caso1" -o figuras/datos/caso1-con-enrutamiento.csv results/Caso1-#0.sca results/Caso1-#0.vec
df = pd.read_csv('figuras/datos/caso1-con-enrutamiento.csv')

vectors = df[df['type'] == 'vector']
buffers = vectors[vectors['name'] == 'Buffer Size']

# Figura 1: nodos fuente
fig1, ax1 = plt.subplots(figsize=(10, 6))
for _, row in buffers.iterrows():
    if 'node[0]' in row['module'] or 'node[2]' in row['module']:
        times = np.fromstring(row['vectime'], sep=' ')
        values = np.fromstring(row['vecvalue'], sep=' ')
        ax1.plot(times, values, label=row['module'])
ax1.set_xlabel('Tiempo (s)')
ax1.set_ylabel('Ocupación del buffer (paquetes)')
ax1.legend()
ax1.grid(axis='y')
fig1.tight_layout()
fig1.savefig('figuras/entrega-final-caso1_buffers_fuentes.png', dpi=300)

# Figura 2: máximo buffer de nodos intermediarios
fig2, ax2 = plt.subplots(figsize=(10, 8))
nodos = []
maximos = []
for _, row in buffers.iterrows():
    values = np.fromstring(row['vecvalue'], sep=' ')
    nodos.append(row['module'].replace('Network.', ''))
    maximos.append(values.max())
ax2.bar(nodos, maximos)
ax2.tick_params(axis='x', rotation=90)
ax2.set_xlabel('Nodo')
ax2.set_ylabel('Ocupación máxima (paquetes)')
fig2.tight_layout()
fig2.savefig('figuras/entrega-final-caso1_buffers_intermediarios.png', dpi=300)

# Figura 3: Delay en node[5]
delays = vectors[(vectors['name'] == 'Delay') & (vectors['module'] == 'Network.node[5].app')]
fig3, ax3 = plt.subplots(figsize=(10, 6))
for _, row in delays.iterrows():
    times = np.fromstring(row['vectime'], sep=' ')
    values = np.fromstring(row['vecvalue'], sep=' ')
    ax3.plot(times, values)
ax3.set_xlabel('Tiempo (s)')
ax3.set_ylabel('Demora (s)')
ax3.grid(axis='y')
fig3.tight_layout()
fig3.savefig('figuras/entrega-final-caso1_delay.png', dpi=300)

# Figura 4: Hops en node[5]
hops = vectors[(vectors['name'] == 'Hops') & (vectors['module'] == 'Network.node[5].app')]
fig4, ax4 = plt.subplots(figsize=(10, 6))
for _, row in hops.iterrows():
   times = np.fromstring(row['vectime'], sep=' ')
   values = np.fromstring(row['vecvalue'], sep=' ')
   ax4.plot(times, values)
ax4.set_xlabel('Tiempo (s)')
ax4.set_ylabel('Saltos')
ax4.grid(axis='y')
fig4.tight_layout()
fig4.savefig('figuras/entrega-final-caso1_hops.png', dpi=300)

# Figura 5: Utilización de enlaces
scalars = df[df['type'] == 'scalar']
link_util = scalars[scalars['name'] == 'Link utilization'].copy()
link_util['node'] = link_util['module'].str.extract(r'(node\[\d+\]\.lnk\[\d+\])')
link_util['value'] = link_util['value'].astype(float)

fig3, ax3 = plt.subplots(figsize=(10, 6))
ax3.bar(link_util['node'], link_util['value'])
ax3.set_xlabel('Enlace')
ax3.set_ylabel('Utilización')
ax3.tick_params(axis='x', rotation=90)
ax3.grid(axis='y')
fig3.tight_layout()
fig3.savefig('figuras/entrega-final-caso1_link_utilization.png', dpi=300)

# Figura 6: Paquetes reenviados por nodo
fwd = scalars[scalars['name'] == 'Forwarded packets'].copy()
fwd['node'] = fwd['module'].str.extract(r'(node\[\d+\])')
fwd['value'] = fwd['value'].astype(float)

fig4, ax4 = plt.subplots(figsize=(10, 6))
ax4.bar(fwd['node'], fwd['value'])
ax4.set_xlabel('Nodo')
ax4.set_ylabel('Paquetes reenviados')
ax4.tick_params(axis='x', rotation=90)
ax4.grid(axis='y')
fig4.tight_layout()
fig4.savefig('figuras/entrega-final-caso1_forwarded.png', dpi=300)

plt.show()
