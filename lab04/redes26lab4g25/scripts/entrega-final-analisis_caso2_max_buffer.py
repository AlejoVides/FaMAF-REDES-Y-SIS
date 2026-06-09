import pandas as pd
import numpy as np

# Generar con: opp_scavetool export -f "runattr:configname =~ Caso2" -o figuras/datos/caso2-con-enrutamiento.csv results/Caso2-*.sca results/Caso2-*.vec
df = pd.read_csv('figuras/datos/caso2-con-enrutamiento.csv')

runatts = df[df['type'] == 'runattr']
iat_map = runatts[runatts['attrname'] == 'iterationvars'][['run', 'attrvalue']]
iat_map = iat_map.rename(columns={'attrvalue': 'iat'})

vectors = df[df['type'] == 'vector']
vectors = vectors.merge(iat_map, on='run', how='left')

buffers = vectors[vectors['name'] == 'Buffer Size']

for iat in sorted(buffers['iat'].unique(), key=lambda x: float(x.replace('$iat=', ''))):
    subset = buffers[buffers['iat'] == iat]
    max_buffer = 0
    for _, row in subset.iterrows():
        values = np.fromstring(row['vecvalue'], sep=' ')
        max_buffer = max(max_buffer, values.max())
    print(f"{iat}: max buffer = {max_buffer}")
    