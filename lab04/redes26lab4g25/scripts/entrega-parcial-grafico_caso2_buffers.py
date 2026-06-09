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

vectors = df[df['type'] == 'vector']
vectors = vectors.merge(iat_map, on='run', how='left')

buffers = vectors[vectors['name'] == 'Buffer Size']

iat_values = sorted(buffers['iat'].unique(), key=lambda x: float(x.replace('$iat=', '')))

for iat in iat_values:
    subset = buffers[buffers['iat'] == iat]
    fig, ax = plt.subplots(figsize=(10, 6))
    for _, row in subset.iterrows():
        times = np.fromstring(row['vectime'], sep=' ')
        values = np.fromstring(row['vecvalue'], sep=' ')
        ax.plot(times, values, label=row['module'].replace('Network.', '').replace('.lnk[0]', ''))
    ax.set_xlabel('Tiempo (s)')
    ax.set_ylabel('Ocupación del buffer (paquetes)')
    ax.legend()
    ax.grid(axis='y')
    fig.tight_layout()
    fig.savefig(f'figuras/caso2_buffers_iat{iat.replace("$iat=", "")}.png', dpi=300)
    plt.close(fig)

print("Gráficos generados.")
