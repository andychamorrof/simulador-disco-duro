"""Planificación de un disco duro: simulación de eventos discretos con SimPy.
Un servidor (el brazo), una cola de pedidos y tres políticas: FCFS, SSTF y LOOK."""
import math, random, statistics
import simpy

C = 1000                                   # cilindros 0..999
SEEK_A, SEEK_B = 0.2381, 0.5619            # búsqueda: a + b·√d  (0,8 ms con d = 1; 18 ms con d = 999)
TAMANOS = [(4, 0.40), (16, 0.30), (64, 0.20), (256, 0.10)]   # KB y probabilidad
TASA_MB_S = 150
EXTRA_ESCRITURA = 0.4                      # ms

def busqueda(d):
    return 0.0 if d == 0 else SEEK_A + SEEK_B * math.sqrt(d)

def tamano(rnd):                           # transformada inversa discreta
    u, acum = rnd.random(), 0.0
    for kb, p in TAMANOS:
        acum += p
        if u < acum:
            return kb
    return TAMANOS[-1][0]

class Disco:
    def __init__(self, env, politica, rpm, rnd):
        self.env, self.politica, self.rnd = env, politica, rnd
        self.vuelta = 60000 / rpm          # ms por vuelta
        self.cola, self.cabeza, self.dir = [], 500, 1
        self.hay_pedido = env.event()
        self.ocupado_ms = 0.0
        self.respuestas = []

    def elegir(self):
        if self.politica == 'FCFS':
            return self.cola.pop(0)
        if self.politica == 'SSTF':
            i = min(range(len(self.cola)), key=lambda k: (abs(self.cola[k]['cil'] - self.cabeza), self.cola[k]['lleg']))
            return self.cola.pop(i)
        for _ in range(2):                 # LOOK: sigue en la dirección actual o invierte
            cand = [k for k, q in enumerate(self.cola) if (q['cil'] - self.cabeza) * self.dir >= 0]
            if cand:
                i = min(cand, key=lambda k: (abs(self.cola[k]['cil'] - self.cabeza), self.cola[k]['lleg']))
                return self.cola.pop(i)
            self.dir = -self.dir

    def brazo(self, calentamiento):        # proceso servidor
        while True:
            if not self.cola:
                self.hay_pedido = self.env.event()
                yield self.hay_pedido
            q = self.elegir()
            d = abs(q['cil'] - self.cabeza)
            if q['cil'] != self.cabeza:
                self.dir = 1 if q['cil'] > self.cabeza else -1
            servicio = busqueda(d) + self.rnd.uniform(0, self.vuelta) + q['kb'] / 1024 / TASA_MB_S * 1000 \
                       + (EXTRA_ESCRITURA if q['escritura'] else 0)
            inicio = self.env.now
            yield self.env.timeout(servicio)
            self.cabeza = q['cil']
            if q['lleg'] >= calentamiento:
                self.respuestas.append(self.env.now - q['lleg'])
                self.ocupado_ms += servicio

def llegadas(env, disco, lam, p_escritura, rnd):   # proceso generador de pedidos
    while True:
        yield env.timeout(rnd.expovariate(lam / 1000))          # ms; Poisson con λ pedidos/s
        disco.cola.append({'lleg': env.now, 'cil': rnd.randrange(C),
                           'escritura': rnd.random() < p_escritura, 'kb': tamano(rnd)})
        if not disco.hay_pedido.triggered:
            disco.hay_pedido.succeed()

def simular(politica='FCFS', lam=50, rpm=7200, p_escritura=0.3, horizonte_s=600, calentamiento_s=60, semilla=42):
    rnd = random.Random(semilla)
    env = simpy.Environment()
    disco = Disco(env, politica, rpm, rnd)
    env.process(llegadas(env, disco, lam, p_escritura, rnd))
    env.process(disco.brazo(calentamiento_s * 1000))
    env.run(until=horizonte_s * 1000)
    r = sorted(disco.respuestas)
    return {'atendidos': len(r), 'W': statistics.mean(r), 'p95': r[int(0.95 * (len(r) - 1))],
            'p99': r[int(0.99 * (len(r) - 1))], 'utilizacion': disco.ocupado_ms / ((horizonte_s - calentamiento_s) * 1000)}

if __name__ == '__main__':
    for pol in ['FCFS', 'SSTF', 'LOOK']:
        r = simular(pol, lam=50)
        print(f"{pol}: {r['atendidos']} pedidos, W = {r['W']:.2f} ms, p95 = {r['p95']:.1f} ms, "
              f"p99 = {r['p99']:.1f} ms, utilización = {r['utilizacion']:.3f}")
