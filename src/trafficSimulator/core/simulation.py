from trafficSimulator.core.intersection import Intersection
from trafficSimulator.core.obstacle import Obstacle
from trafficSimulator.core.static_object import StaticObject
from trafficSimulator.core.traffic_light import TrafficLight
from .vehicle_generator import VehicleGenerator
from .geometry.quadratic_curve import QuadraticCurve
from .geometry.cubic_curve import CubicCurve
from .geometry.segment import Segment
from .vehicle import Vehicle
from scipy.spatial import distance
import heapq # Per l'algoritmo di Dijkstra


class Simulation:
    def __init__(self):
        self.segments = []
        self.vehicles = {}
        self.vehicle_generator = []
        self.static_objects = [] 
        self.obstacles = []
        self.intersections = []
        self.traffic_lights = []

        self.t = 0.0
        self.frame_count = 0
        self.dt = 1/60  


    def add_vehicle(self, veh):
        self.vehicles[veh.id] = veh
        if len(veh.path) > 0:
            self.segments[veh.path[0]].add_vehicle(veh)

    def add_segment(self, seg):
        self.segments.append(seg)

    def add_vehicle_generator(self, gen):
        self.vehicle_generator.append(gen)

    def create_vehicle(self, **kwargs):
        veh = Vehicle(kwargs)
        self.add_vehicle(veh)

    def create_segment(self, *args, **kwargs):
        seg = Segment(args, **kwargs)
        self.add_segment(seg)
        return seg

    def create_quadratic_bezier_curve(self, start, control, end, **kwargs):
        cur = QuadraticCurve(start, control, end, **kwargs)
        self.add_segment(cur)

    def create_cubic_bezier_curve(self, start, control_1, control_2, end, **kwargs):
        cur = CubicCurve(start, control_1, control_2, end, **kwargs)
        self.add_segment(cur)

    def create_vehicle_generator(self, **kwargs):
        # Se nella configurazione ci sono veicoli definiti, controlliamo se serve calcolare il percorso
        if 'vehicles' in kwargs:
            for i, (weight, config) in enumerate(kwargs['vehicles']):
                # Se mancano le istruzioni path, ma ci sono start_road e end_road
                if 'path' not in config and 'start_road' in config and 'end_road' in config:
                    try:
                        # Calcoliamo il percorso usando la topologia attuale
                        path = self.find_shortest_path(config['start_road'], config['end_road'])
                        config['path'] = path
                        print(f"Path calcolato per veicolo {config.get('vehicle_class', 'unknown')}: {path}")
                    except Exception as e:
                        print(f"Errore nel calcolo del percorso: {e}")
                        config['path'] = []

        gen = VehicleGenerator(kwargs)
        self.add_vehicle_generator(gen)

    def create_static_object(self, x, y, width, height, color, shape="rectangle"):
        obj = StaticObject(x, y, width, height, color, shape)
        self.static_objects.append(obj)

    def create_obstacle(self, segment_id, position, duration):
        # segment_id è l'indice numerico del segmento nella lista self.segments
        obs = Obstacle(segment_id, position, duration)
        self.obstacles.append(obs)
    
    def create_traffic_light(self, segment_id, position, cycle_time=5, initial_state="red"):
        # Passiamo initial_state al costruttore di TrafficLight
        tl = TrafficLight(segment_id, position, cycle_time, initial_state)
        self.traffic_lights.append(tl)
        return tl
    
    def create_intersection(self, x, y, id_inter="", size=20):
        # Nota: Non passiamo più **kwargs per ora per semplicità
        inter = Intersection(self, x, y, id_inter, size)
        self.intersections.append(inter)
        return inter

    def run(self, steps):
        for _ in range(steps):
            self.update()

    def _build_topology(self):
        """
        Costruisce il grafo delle connessioni tra segmenti basandosi sulla geometria.
        Due segmenti sono connessi se la fine di uno coincide con l'inizio dell'altro.
        """
        self.adjacency_list = {i: [] for i in range(len(self.segments))}
        self.segment_id_map = {} # Mappa da ID stringa a indice numerico

        # 1. Costruisci la mappa degli ID
        for i, seg in enumerate(self.segments):
            if hasattr(seg, 'id_segment') and seg.id_segment:
                self.segment_id_map[seg.id_segment] = i
        
        # 2. Trova le connessioni (N^2, ma ok per simulazioni piccole)
        # Tolleranza di 0.1 metri per considerare i punti "uniti"
        tolerance = 0.5 
        
        for i, seg_a in enumerate(self.segments):
            end_point = seg_a.points[-1]
            
            for j, seg_b in enumerate(self.segments):
                if i == j: continue # Non collegarsi a se stessi
                
                start_point = seg_b.points[0]
                dist = distance.euclidean(end_point, start_point)
                
                if dist < tolerance:
                    self.adjacency_list[i].append(j)
    
    def find_shortest_path(self, start_id, end_id):
        """
        Trova il percorso più breve tra due segmenti usando i loro ID stringa.
        Restituisce una lista di indici [idx1, idx2, idx3...]
        """
        # Costruiamo la topologia se non esiste o se sono stati aggiunti segmenti
        # Nota: per efficienza potresti farlo solo una volta alla fine della creazione
        self._build_topology()

        if start_id not in self.segment_id_map:
            raise ValueError(f"Start segment ID '{start_id}' not found.")
        if end_id not in self.segment_id_map:
            raise ValueError(f"End segment ID '{end_id}' not found.")

        start_idx = self.segment_id_map[start_id]
        end_idx = self.segment_id_map[end_id]

        # Dijkstra Algorithm
        # coda: (costo, nodo_corrente, percorso_fino_a_qui)
        queue = [(0, start_idx, [])]
        visited = set()
        
        while queue:
            (cost, current_idx, path) = heapq.heappop(queue)
            
            if current_idx in visited:
                continue
            visited.add(current_idx)

            # Percorso aggiornato
            path = path + [current_idx]

            # Trovato!
            if current_idx == end_idx:
                return path

            # Esplora vicini
            for neighbor in self.adjacency_list[current_idx]:
                if neighbor not in visited:
                    # Il costo è la lunghezza del segmento (cerchiamo il percorso più corto in metri)
                    # Oppure 1 (per il minor numero di segmenti)
                    weight = self.segments[neighbor].get_length()
                    heapq.heappush(queue, (cost + weight, neighbor, path))

        print(f"Nessun percorso trovato tra {start_id} e {end_id}")
        return []
    
    def update(self):
        # 1. Aggiorna ostacoli e semafori
        for obs in self.obstacles:
            obs.update(self.dt)
        for tl in self.traffic_lights:
            tl.update(self.dt)
            
        # Rimuovi ostacoli scaduti (ma non i semafori, quelli restano!)
        self.obstacles = [obs for obs in self.obstacles if obs.active]

        # 2. Aggiorna veicoli
        for segment_index, segment in enumerate(self.segments):
            # Troviamo gli ostacoli su questo segmento
            obs_on_segment = [obs for obs in self.obstacles if obs.segment_id == segment_index]
            
            # Troviamo i semafori ROSSI su questo segmento
            lights_on_segment = [tl for tl in self.traffic_lights if tl.segment_id == segment_index and tl.is_active]
            
            # Uniamo tutto ciò che blocca la strada in un'unica lista "barriere"
            # Entrambi gli oggetti (Obstacle e TrafficLight) hanno 'x' e devono essere trattati come fermi.
            barriers = obs_on_segment + lights_on_segment
            
            # --- NUOVO: Rilevamento Incrocio e Precedenza ---
            # Cerchiamo se questo segmento fa parte di un incrocio come "incoming"
            parent_intersection = None
            for inter in self.intersections:
                # Usiamo l'oggetto segmento per trovarlo
                if segment in inter.incoming_roads:
                    parent_intersection = inter
                    break
            
            intersection_barrier = None
            
            for i, vehicle_id in enumerate(segment.vehicles):
                vehicle = self.vehicles[vehicle_id]
                
                # Se c'è un incrocio alla fine di questa strada
                if parent_intersection:
                    # Controlliamo solo se siamo vicini alla fine (es. ultimi 15 metri)
                    dist_to_end = segment.get_length() - vehicle.x
                    
                    if dist_to_end < 15:
                        # Chiediamo all'incrocio se è libero
                        is_clear = parent_intersection.check_clearance(vehicle, segment_index)
                        
                        if not is_clear:
                            # Creiamo una barriera virtuale alla fine della strada
                            # Creiamo un oggetto "dummy" che si comporta come un ostacolo
                            class VirtualBarrier:
                                def __init__(self, x):
                                    self.x = x
                                    self.v = 0
                                    self.l = 0 # Puntiforme (o vehicle.l per stop line)
                            
                            # Posizione: fine strada
                            intersection_barrier = VirtualBarrier(segment.get_length())
                            
                            # Per lo STOP, vogliamo fermarci col muso alla linea
                            # Se è uno STOP sign, settiamo la lunghezza barrier = veicolo (come abbiamo fatto per semafori)
                            if segment_index in parent_intersection.stop_signs:
                                intersection_barrier.l = vehicle.l

                # --- FINE NUOVO ---

                # Calcolo Lead (chi sta davanti)
                lead = None
                
                # 1. Veicolo davanti
                if i > 0:
                    lead = self.vehicles[segment.vehicles[i-1]]
                
                # 2. Barriere Fisiche (Semafori/Ostacoli) - Codice precedente
                vehicle_front_pos = vehicle.x + vehicle.l
                relevant_barriers = [b for b in barriers if b.x > vehicle_front_pos]
                
                # 3. Barriera Virtuale Incrocio (Precedenza/Stop)
                # Se esiste ed è davanti al muso, la aggiungiamo
                if intersection_barrier and intersection_barrier.x > vehicle_front_pos:
                    relevant_barriers.append(intersection_barrier)

                # Trova la barriera più vicina
                if relevant_barriers:
                    closest_barrier = min(relevant_barriers, key=lambda b: b.x)
                    
                    # Logica stop line (l = vehicle.l) se non settata
                    if not hasattr(closest_barrier, 'v'): closest_barrier.v = 0
                    if not hasattr(closest_barrier, 'l'): closest_barrier.l = 0
                    
                    if lead:
                        if closest_barrier.x < lead.x:
                            lead = closest_barrier
                    else:
                        lead = closest_barrier

                vehicle.update(lead, self.dt)
                
                # Pulizia per veicoli che hanno superato l'incrocio: rimuovere da "stopped_vehicles"
                if parent_intersection and vehicle.id in parent_intersection.stopped_vehicles:
                     # Se è passato all'altro segmento (non è più su questo), lo rimuoviamo
                     # Ma qui siamo dentro il loop di QUESTO segmento. 
                     # Se è ancora qui ma ha velocità > 2, vuol dire che è ripartito -> Reset
                     if vehicle.v > 2:
                         parent_intersection.stopped_vehicles.remove(vehicle.id)
                
        # --- (Riporto la parte finale per completezza) ---
        for segment in self.segments:
            if len(segment.vehicles) == 0: continue
            vehicle_id = segment.vehicles[0]
            vehicle = self.vehicles[vehicle_id]
            if vehicle.x >= segment.get_length():
                if vehicle.current_road_index + 1 < len(vehicle.path):
                    vehicle.current_road_index += 1
                    next_road_index = vehicle.path[vehicle.current_road_index]
                    self.segments[next_road_index].vehicles.append(vehicle_id)
                vehicle.x = 0
                segment.vehicles.popleft() 

        for gen in self.vehicle_generator:
            gen.update(self)
        self.t += self.dt
        self.frame_count += 1
