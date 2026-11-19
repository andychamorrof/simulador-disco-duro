# Planificación de un disco duro: simulación de FCFS, SSTF y LOOK

Simulador web de eventos discretos para el curso **Modelos y Simulación** (Escuela Profesional de Ciencias de la Computación, UNMSM).

**Abrir el simulador:** https://andychamorrof.github.io/simulador-disco-duro/

## El modelo

El sistema es una cola con un solo servidor:

- **Entidades:** los pedidos de lectura y escritura.
- **Servidor:** el brazo del disco.
- **Disciplina de atención:** la decide una política de planificación.
  - **FCFS:** atiende por orden de llegada.
  - **SSTF:** atiende el pedido más cercano al brazo.
  - **LOOK:** el brazo barre en un sentido y luego regresa, como un ascensor.

| Variable aleatoria | Distribución |
|---|---|
| Tiempo entre llegadas | Exponencial(λ), es decir, llegadas de Poisson |
| Cilindro pedido | Uniforme discreta {0, …, 999} (o una mezcla 80/20 con localidad) |
| Tipo de operación | Bernoulli (probabilidad de escritura = 0,30) |
| Tamaño del pedido | Discreta empírica: 4 / 16 / 64 / 256 KB con probabilidades 0,4 / 0,3 / 0,2 / 0,1 |
| Latencia rotacional | Uniforme(0, 60 000 / RPM) ms |

- **Tiempo de búsqueda:** a + b·√d ms, donde d es la distancia en cilindros.
- **Transferencia:** tamaño / 150 MB/s, más 0,4 ms si es escritura.

## Vistas del simulador

1. **En vivo:** el flujo animado del proceso, el disco y el recorrido del brazo de cada política.
2. **Resultados:** 10 minutos simulados, sin el calentamiento. Incluye el desglose del tiempo de respuesta, los percentiles y la equidad por zona del disco.
3. **Paso a paso:** las rutinas de eventos, la lista de eventos futuros, las variables de estado, Q(t) y la traza de eventos.
4. **Validación:** la comparación con la teoría M/G/1 (Pollaczek-Khinchine), la curva de carga, los histogramas de los generadores y las réplicas con intervalos de confianza al 95 %.

Las tres políticas usan **números aleatorios comunes**: los mismos pedidos, generados con un PRNG con semilla y un flujo independiente para cada variable.

## Archivos

- `index.html`: el simulador completo, en un solo archivo y sin dependencias.
- `sim_disco.py`: la implementación equivalente en Python con SimPy, usada para la validación cruzada.

## Autor

Chamorro Figueroa, Andy Aaron · Docente: Rivas Peña, Marcos Hernan · Lima, Perú, 2026
