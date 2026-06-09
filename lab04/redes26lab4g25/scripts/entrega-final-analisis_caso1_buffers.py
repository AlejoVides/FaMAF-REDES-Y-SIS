import pandas as pd
import numpy as np

# Generar con: opp_scavetool export -f "runattr:configname =~ Caso1" -o figuras/datos/caso1-con-enrutamiento.csv results/Caso1-#0.sca results/Caso1-#0.vec
df = pd.read_csv('figuras/datos/caso1-con-enrutamiento.csv')

vectors = df[df['type'] == 'vector']
buffer_vectors = vectors[vectors['name'] == 'Buffer Size'].copy()

for _, row in buffer_vectors.iterrows():
    values = np.array(list(map(float, row['vecvalue'].split())))
    print(f"{row['module']}")
    print(f"  mean:   {values.mean():.4f}")
    print(f"  max:    {values.max():.0f}")
    print(f"  stddev: {values.std():.4f}")
    print()
    