import pandas as pd

# Generar con: opp_scavetool export -f "runattr:configname =~ Caso2" -o figuras/datos/caso2.csv results/Caso2-*.sca results/Caso2-*.vec
df = pd.read_csv('figuras/datos/caso2.csv')

runatts = df[df['type'] == 'runattr']
iat_map = runatts[runatts['attrname'] == 'iterationvars'][['run', 'attrvalue']]
iat_map = iat_map.rename(columns={'attrvalue': 'iat'})

vectors = df[df['type'] == 'vector']
vectors = vectors.merge(iat_map, on='run', how='left')

print(vectors[['iat', 'module', 'name']].to_string())
