import math
from .geometry.segment import Segment
from .geometry.quadratic_curve import QuadraticCurve

class Intersection:
    def __init__(self, simulation, x, y, id_inter, size=20):
        self.sim = simulation
        self.x = x
        self.y = y
        self.id = id_inter
        self.size = size
        
        # Liste di segmenti esterni
        self.incoming_roads = []
        self.outgoing_roads = []
        
        # Mappa dei percorsi interni: self.paths[id_entrata][id_uscita] = segmento
        self.paths = {} 
        
        # --- Gestione Priorità e Stop ---
        self.stop_signs = {}  # {segment_index: True}
        self.priority_map = {} # {segment_index: [lista_indici_prioritari]}
        self.stopped_vehicles = set() # {vehicle_id}

    def add_incoming(self, segment):
        """Registra una strada che ARRIVA all'incrocio"""
        self.incoming_roads.append(segment)
        if segment.id_segment not in self.paths:
            self.paths[segment.id_segment] = {}

    def add_outgoing(self, segment):
        """Registra una strada che PARTE dall'incrocio"""
        self.outgoing_roads.append(segment)

    def add_stop_sign(self, road):
        """Aggiunge un segnale di STOP alla strada specificata"""
        try:
            seg_index = self.sim.segments.index(road)
            self.stop_signs[seg_index] = True
        except ValueError:
            print(f"Warning: Road {road.id_segment} not found in simulation.")

    def set_traffic_lights(self, cycle_time=10):
        """Aggiunge semafori automatici (Verde Nord-Sud, Rosso Est-Ovest)"""
        vertical_roads = []
        horizontal_roads = []

        for road in self.incoming_roads:
            p1 = road.points[-2]
            p2 = road.points[-1]
            angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
            
            if abs(math.sin(angle)) > abs(math.cos(angle)):
                vertical_roads.append(road)
            else:
                horizontal_roads.append(road)

        for road in vertical_roads:
            self._add_light_to_road(road, cycle_time, "green")
        for road in horizontal_roads:
            self._add_light_to_road(road, cycle_time, "red")

    def _add_light_to_road(self, road, cycle_time, initial_state):
        pos = road.get_length() - 2
        if pos < 0: pos = 0
        try:
            seg_index = self.sim.segments.index(road)
            self.sim.create_traffic_light(seg_index, pos, cycle_time, initial_state)
        except ValueError:
            pass

    def build(self):
        """Genera le connessioni interne"""
        for road_in in self.incoming_roads:
            for road_out in self.outgoing_roads:
                self._create_connection(road_in, road_out)

    def _create_connection(self, road_in, road_out):
        p_start = road_in.points[-1]
        p_end = road_out.points[0]
        
        v_in = (road_in.points[-1][0] - road_in.points[-2][0], 
                road_in.points[-1][1] - road_in.points[-2][1])
        v_out = (road_out.points[1][0] - road_out.points[0][0], 
                 road_out.points[1][1] - road_out.points[0][1])
        
        ang_in = math.atan2(v_in[1], v_in[0])
        ang_out = math.atan2(v_out[1], v_out[0])
        
        diff = abs(ang_in - ang_out)
        while diff > math.pi: diff -= 2*math.pi
        while diff < -math.pi: diff += 2*math.pi
        
        seg_id = f"{self.id}_from_{road_in.id_segment}_to_{road_out.id_segment}"
        
        if abs(diff) < 0.1: 
            self.sim.create_segment(p_start, p_end, category="intersection", id_segment=seg_id)
        else:
            control_point = ((p_start[0]+p_end[0])/2, (p_start[1]+p_end[1])/2)
            # Logica semplice: se è una svolta a destra o sinistra, spostiamo il control point
            # Per ora il punto medio funziona decentemente come approssimazione
            self.sim.create_quadratic_bezier_curve(p_start, control_point, p_end, category="intersection", id_segment=seg_id)
        
        new_segment = self.sim.segments[-1]
        self.paths[road_in.id_segment][road_out.id_segment] = new_segment

    def _get_road_angle(self, road):
        p1 = road.points[-2]
        p2 = road.points[-1]
        return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

    def calculate_priorities(self):
        """Costruisce la mappa delle precedenze"""
        for road_a in self.incoming_roads:
            try:
                idx_a = self.sim.segments.index(road_a)
            except ValueError:
                continue

            angle_a = self._get_road_angle(road_a)
            self.priority_map[idx_a] = []

            # CASO 1: Ho lo STOP -> Precedenza a tutti
            if idx_a in self.stop_signs:
                for road_b in self.incoming_roads:
                    if road_a == road_b: continue
                    try:
                        idx_b = self.sim.segments.index(road_b)
                        self.priority_map[idx_a].append(idx_b)
                    except ValueError:
                        continue
                continue

            # CASO 2: Non ho STOP -> Precedenza a destra
            for road_b in self.incoming_roads:
                if road_a == road_b: continue
                try:
                    idx_b = self.sim.segments.index(road_b)
                    
                    # Se l'altro ha STOP, lo ignoro (lui aspetta me)
                    if idx_b in self.stop_signs:
                        continue

                    angle_b = self._get_road_angle(road_b)
                    
                    diff = angle_a - angle_b
                    while diff > math.pi: diff -= 2*math.pi
                    while diff <= -math.pi: diff += 2*math.pi
                    
                    # Se diff è positivo (~PI/2), B è alla mia destra
                    if 0.5 < diff < 2.5:
                        self.priority_map[idx_a].append(idx_b)

                except ValueError:
                    continue

    def check_clearance(self, vehicle, segment_index):
        # 1. STOP SIGN
        if segment_index in self.stop_signs:
            if vehicle.id not in self.stopped_vehicles:
                if vehicle.v < 0.5:
                     self.stopped_vehicles.add(vehicle.id)
                     # Si è fermato, ora controlla se è libero
                else:
                    return False # Deve ancora fermarsi
        
        # 2. Controllo Strade Prioritarie
        priority_segments = self.priority_map.get(segment_index, [])
        scan_distance = 40 
        
        for other_idx in priority_segments:
            other_seg = self.sim.segments[other_idx]
            for veh_id in other_seg.vehicles:
                other_veh = self.sim.vehicles[veh_id]
                dist_to_inter = other_seg.get_length() - other_veh.x
                
                if dist_to_inter < scan_distance and other_veh.v > 0.5:
                    return False # Qualcuno sta arrivando da una strada prioritaria
                    
        return True