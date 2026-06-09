# Laboratorio 3: Transporte
## Redes y Sistemas Distribuidos · FaMAF

## Integrantes

- Gerbaudo, Nicolas Ignacio
- Jorge Gonzalez, Nicolas
- Ontivero, Nahuel Mauricio
- Vides, Alejo Miguel

Ubicación del informe: `./Informe.md`

## Descripción

En este laboratorio se estudian problemas de transporte usando modelos de red simulados en OMNeT++. Se analizan dos escenarios con distinto cuello de botella: control de flujo (Caso 1, buffer del receptor saturado) y control de congestión (Caso 2, cola intermedia saturada). En la Parte 2 se implementa un algoritmo de control inspirado en TCP usando ventanas de congestión (`cwnd`) y recepción (`rwnd`) con feedback explícito de congestión (ECN).

## Compilar

```sh
make
```

## Correr simulaciones

### Parte 1 (sin control)

Ir al commit de la entrega parcial:

```sh
git switch --detach v0.1-parte1
make
./lab3-kickstarter -u Cmdenv -c Caso1
./lab3-kickstarter -u Cmdenv -c Caso2
```

### Parte 2 (con control)

```sh
git switch main
make
./lab3-kickstarter -u Cmdenv -c Caso1
./lab3-kickstarter -u Cmdenv -c Caso2
```

### Competición

```sh
./lab3-kickstarter -u Cmdenv -c Competicion
```

## Resultados de la Competición

| Grupo | goodput (pkt/s) | lossRate (%) | avgDelay (s) | stability (pkt) |
|-------|-----------------|--------------|--------------|-----------------|
| Grupo 25 | 4.985 | 0% | 6.067 | 10.614 |

