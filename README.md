# Traffic Simulator Project

Questo progetto è una libreria Python per la simulazione del traffico veicolare. Permette di creare reti stradali complesse, definire diverse tipologie di veicoli, gestire il flusso del traffico e visualizzare la simulazione in tempo reale.

## Installazione

Assicurati di avere Python installato. Installa le dipendenze necessarie:

```bash
pip install -r requirements.txt
```

## Guida Rapida

Ecco un esempio minimale per avviare una simulazione:

```python
from trafficSimulator import *

# 1. Crea la simulazione
sim = Simulation()

# 2. Aggiungi strade (Segmenti)
# Coordinate (x, y)
sim.create_segment((0, 0), (100, 0))

# 3. Aggiungi un generatore di veicoli
vg = VehicleGenerator({
    'vehicle_rate': 20, # veicoli al minuto
    'vehicles': [
        (1, {'path': [0]}) # Peso 1, percorso sul segmento 0
    ]
})
sim.add_vehicle_generator(vg)

# 4. Avvia la visualizzazione
win = Window(sim)
win.run()
win.show()
```

## Elementi della Simulazione

Di seguito sono descritti in dettaglio tutti gli elementi che è possibile creare e configurare.

### 1. Simulazione (`Simulation`)

È il contenitore principale di tutti gli elementi. Gestisce l'aggiornamento della fisica e lo stato del mondo.

```python
sim = Simulation()
```

### 2. Rete Stradale

Le strade sono composte da segmenti connessi. Ogni segmento ha una direzione (dal punto di inizio al punto di fine).

#### Segmenti Rettilinei (`create_segment`)

Collegano due punti con una linea retta.

```python
# create_segment(start_point, end_point, **kwargs)
sim.create_segment((0, 0), (100, 0), max_speed=50)
```

#### Curve di Bézier Quadratiche (`create_quadratic_bezier_curve`)

Curve definite da un punto di inizio, un punto di controllo e un punto di fine. Utili per curve a 90 gradi o svolte morbide.

```python
# create_quadratic_bezier_curve(start, control, end, **kwargs)
sim.create_quadratic_bezier_curve((100, 0), (150, 0), (150, 50))
```

#### Curve di Bézier Cubiche (`create_cubic_bezier_curve`)

Curve più complesse definite da due punti di controllo. Utili per forme a "S" o raccordi complessi.

```python
# create_cubic_bezier_curve(start, control1, control2, end, **kwargs)
sim.create_cubic_bezier_curve((0, 0), (50, 0), (50, 50), (100, 50))
```

**Proprietà Comuni delle Strade:**
Tutti i metodi di creazione strada accettano argomenti opzionali (`kwargs`):

- `max_speed`: Velocità massima sul segmento (default: 50).
- `category`: Categoria della strada (es. "urban", "highway").
- `id_segment`: Identificativo univoco (stringa) utile per definire percorsi tramite ID invece che indici numerici.

### 3. Veicoli (`Vehicle`)

I veicoli sono gli agenti che si muovono sulla rete. Possono essere configurati con molte proprietà fisiche e logiche.

**Proprietà Configurabili:**

- `l`: Lunghezza (default: 4)
- `w`: Larghezza (default: 2)
- `v_max`: Velocità massima (m/s)
- `vehicle_class`: Tipo ("car", "truck", "bus", "motorcycle")
- `engine_type`: Motore ("combustion", "electric", "hybrid")
- `path`: Lista di ID o indici dei segmenti da percorrere.

Esempio di creazione manuale (raro, meglio usare i generatori):

```python
sim.create_vehicle(
    vehicle_class="truck",
    l=8,
    path=[0, 1, 2]
)
```

### 4. Generatori di Veicoli (`VehicleGenerator`)

I generatori creano veicoli automaticamente a intervalli regolari.

```python
vg = VehicleGenerator({
    'vehicle_rate': 15, # Veicoli al minuto
    'vehicles': [
        # (Peso, Configurazione Veicolo)
        (10, {'vehicle_class': 'car', 'path': [0, 1]}),
        (1,  {'vehicle_class': 'truck', 'l': 8, 'path': [0, 1]})
    ]
})
sim.add_vehicle_generator(vg)
```

Il `Peso` determina la probabilità che venga generato quel tipo di veicolo. Nell'esempio sopra, c'è una probabilità 10:1 di generare un'auto rispetto a un camion.

### 5. Oggetti Statici (`StaticObject`)

Elementi decorativi o strutturali come edifici, parchi o aree. Non interagiscono con il traffico ma arricchiscono la visualizzazione.

```python
# create_static_object(x, y, width, height, color, shape)
sim.create_static_object(50, 50, 20, 20, (100, 100, 100), shape="rectangle")
```

### 6. Ostacoli (`Obstacle`)

Blocchi temporanei su un segmento stradale, utili per simulare incidenti o lavori in corso.

```python
# create_obstacle(segment_id, position, duration)
# segment_id: indice numerico del segmento
# position: distanza dall'inizio del segmento
# duration: durata in frame (o tempo simulato)
sim.create_obstacle(0, 50, 200)
```

### 7. Semafori (`TrafficLight`)

È possibile aggiungere semafori manuali su specifici segmenti. I semafori alternano lo stato tra Rosso e Verde.

```python
# create_traffic_light(segment_id, position, cycle_time, initial_state)
# segment_id: indice del segmento
# position: posizione in metri
# cycle_time: durata del ciclo (es. 10 secondi)
sim.create_traffic_light(0, 90, cycle_time=10, initial_state="red")
```

### 8. Incroci Avanzati (`Intersection`)

La classe `Intersection` permette di gestire incroci complessi con logiche di precedenza, stop e semafori automatici.

```python
# 1. Crea l'incrocio
inter = sim.create_intersection(0, 0, id_inter="crossroad", size=20)

# 2. Aggiungi strade (devono essere segmenti esistenti)
inter.add_incoming(seg_south_in)
inter.add_outgoing(seg_south_out)
# ... aggiungi altre strade ...

# 3. Configura regole
# Aggiunge un segnale di STOP su una strada specifica
inter.add_stop_sign(seg_south_in)

# OPPURE: Configura semafori automatici su tutte le strade entranti
# (Verde per asse verticale, Rosso per orizzontale, alternati)
inter.set_traffic_lights(cycle_time=15)

# 4. Costruisci connessioni interne
# Genera automaticamente i segmenti di connessione interni all'incrocio
inter.build()
```

## Configurazione tramite JSON

È possibile caricare un'intera simulazione da un file JSON usando `ConfigLoader`.

Esempio `config.json`:

```json
{
  "segments": [
    {
      "type": "line",
      "start": [0, 0],
      "end": [100, 0],
      "max_speed": 60,
      "id": "road_A"
    },
    {
      "type": "quadratic",
      "start": [100, 0],
      "control": [150, 0],
      "end": [150, 50],
      "id": "curve_B"
    }
  ],
  "vehicle_generators": [
    {
      "vehicle_rate": 10,
      "vehicles": [[1, { "path": ["road_A", "curve_B"], "v_max": 20 }]]
    }
  ]
}
```

Caricamento in Python:

```python
from trafficSimulator import ConfigLoader

loader = ConfigLoader()
sim, config = loader.load_from_file('config.json')
```

## Visualizzazione

La classe `Window` gestisce la finestra grafica.

```python
win = Window(sim)
win.zoom = 5 # Imposta lo zoom iniziale
win.run()
win.show()
```

Comandi da tastiera (se implementati nel visualizzatore):

- Spesso `Space` mette in pausa/riprendere.
- Mouse per trascinare/zoomare (dipende dall'implementazione specifica di `Window`).
