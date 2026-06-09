import pandas as pd

# Generar con: opp_scavetool export -f "runattr:configname =~ Caso1" -o figuras/datos/caso1-con-enrutamiento.csv results/Caso1-#0.sca results/Caso1-#0.vec
df = pd.read_csv('figuras/datos/caso1-con-enrutamiento.csv')

vectors = df[df['type'] == 'vector']
print(vectors[['module', 'name']].to_string())
