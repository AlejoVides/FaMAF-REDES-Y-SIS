import pandas as pd

# Generar con: opp_scavetool export -f "runattr:configname =~ Caso1" -o figuras/datos/caso1.csv results/Caso1-#0.sca results/Caso1-#0.vec
df = pd.read_csv('figuras/datos/caso1.csv')

scalars = df[df['type'] == 'scalar']
print(scalars[['module', 'name', 'value']].to_string())
