from .geometry.segment import Segment
from .geometry.quadratic_curve import QuadraticCurve
import math

class Intersection:
    def __init__(self, simulation, x, y, id_inter, size=20):
        self.sim = simulation
        self.x = x
        self.y = y
        self.id = id_inter
        self.size = size  # Raggio o dimensione dell'area dell'incrocio
        
        # Liste di segmenti esterni collegati all'incrocio
        # Struttura: {"id_strada": oggetto_segmento}
        self.incoming_roads = []
        self.outgoing_roads = []
        
        # Mappa dei percorsi interni generati
        # self.paths[id_entrata][id_uscita] = oggetto_segmento_interno
        self.paths = {} 

    def add_incoming(self, segment):
        """Registra una strada che ARRIVA all'incrocio"""
        self.incoming_roads.append(segment)
        # Inizializza il dizionario per questo ingresso
        if segment.id_segment not in self.paths:
            self.paths[segment.id_segment] = {}

    def add_outgoing(self, segment):
        """Registra una strada che PARTE dall'incrocio"""
        self.outgoing_roads.append(segment)

    def build(self):
        """
        Genera automaticamente le connessioni (curve/rette) tra 
        tutte le strade in entrata e tutte le strade in uscita.
        """
        for road_in in self.incoming_roads:
            for road_out in self.outgoing_roads:
                # Evitiamo le inversioni a U sulla stessa via (opzionale)
                # Se road_in e road_out sono "opposte" ma vicine, potremmo volerle escludere
                # Per ora colleghiamo TUTTO a TUTTO.
                
                self._create_connection(road_in, road_out)

    def _create_connection(self, road_in, road_out):
        """Crea un segmento interno che collega la fine di road_in all'inizio di road_out"""
        
        # Punti di ancoraggio
        p_start = road_in.points[-1] # Fine della strada in entrata
        p_end = road_out.points[0]   # Inizio della strada in uscita
        
        # Calcoliamo l'angolo di ingresso e uscita per capire se è dritto o curva
        # Vettore strada in entrata (ultimi due punti)
        v_in = (road_in.points[-1][0] - road_in.points[-2][0], 
                road_in.points[-1][1] - road_in.points[-2][1])
        
        # Vettore strada in uscita (primi due punti)
        v_out = (road_out.points[1][0] - road_out.points[0][0], 
                 road_out.points[1][1] - road_out.points[0][1])
        
        # Calcolo angoli
        ang_in = math.atan2(v_in[1], v_in[0])
        ang_out = math.atan2(v_out[1], v_out[0])
        
        diff = abs(ang_in - ang_out)
        # Normalizziamo differenza
        while diff > math.pi: diff -= 2*math.pi
        while diff < -math.pi: diff += 2*math.pi
        
        # ID univoco per il segmento interno
        # Es: "inter_X_from_STRADA1_to_STRADA2"
        seg_id = f"{self.id}_from_{road_in.id_segment}_to_{road_out.id_segment}"
        
        # Se l'angolo è simile (vicino a 0), andiamo DRITTO con una linea
        if abs(diff) < 0.1: 
            self.sim.create_segment(p_start, p_end, category="intersection", id_segment=seg_id)
        else:
            # Altrimenti creiamo una CURVA
            # Calcolo euristico del Control Point per la curva di Bezier
            # Intersezione tra la retta uscente da P_start e la retta entrante in P_end (al contrario)
            
            # Per semplicità, usiamo una media pesata o il centro dell'incrocio come attrattore
            # Un buon control point per curve a 90 gradi è l'angolo del quadrato.
            # Qui usiamo un'approssimazione: prolunghiamo i vettori e vediamo dove si incontrano.
            
            # Controllo semplice: Centro dell'incrocio (self.x, self.y) + offset?
            # Usiamo l'intersezione delle tangenti per una curva perfetta
            control_point = self._calculate_intersection_point(p_start, ang_in, p_end, ang_out)
            
            # Se il calcolo fallisce (rette parallele), usiamo il punto medio
            if control_point is None:
                 control_point = ((p_start[0]+p_end[0])/2, (p_start[1]+p_end[1])/2)

            self.sim.create_quadratic_bezier_curve(p_start, control_point, p_end, category="intersection", id_segment=seg_id)
        
        # Registriamo il segmento creato
        new_segment = self.sim.segments[-1]
        self.paths[road_in.id_segment][road_out.id_segment] = new_segment

    def _calculate_intersection_point(self, p1, theta1, p2, theta2):
        """Trova l'intersezione tra due rette definite da punto e angolo"""
        # Rette: y - y0 = m(x - x0)  ->  -mx + y = y0 - mx0
        # Ma dobbiamo gestire le linee verticali.
        
        sin1, cos1 = math.sin(theta1), math.cos(theta1)
        sin2, cos2 = math.sin(theta2 - math.pi), math.cos(theta2 - math.pi) # Retta 2 va all'indietro per trovare l'angolo

        # Usiamo geometria vettoriale. 
        # P = p1 + t * v1
        # Q = p2 + u * v2
        # Vogliamo P = Q
        
        # Questo è complesso per un forum. Usiamo un'euristica robusta:
        # Il control point è l'angolo del rettangolo che racchiude start e end, 
        # scelto in base alla direzione.
        
        # Oppure, semplicemente estendiamo p1 nella sua direzione e p2 nella sua direzione opposta
        # finché non si incontrano.
        
        # Semplificazione estrema che funziona spesso negli incroci urbani:
        # Se svolta a DESTRA o SINISTRA, il control point è "l'angolo".
        # Control Point x = p_end.x se p1 è orizzontale, p1.x se p1 è verticale...
        
        # Proviamo l'intersezione vera (Cramer)
        # Retta 1: a1*x + b1*y = c1
        # m = tan(theta). -sin*x + cos*y = -sin*x0 + cos*y0
        a1, b1 = -sin1, cos1
        c1 = a1*p1[0] + b1*p1[1]
        
        # Retta 2 (tangente all'arrivo): Angolo è theta2 + 180 (perché entra)
        a2, b2 = -math.sin(theta2), math.cos(theta2)
        c2 = a2*p2[0] + b2*p2[1] # Nota: usiamo tangente in arrivo, quindi stessa retta di road_out
        
        det = a1*b2 - a2*b1
        if abs(det) < 1e-5: return None # Parallele
        
        cx = (c1*b2 - c2*b1) / det
        cy = (a1*c2 - a2*c1) / det
        return (cx, cy)
    

    def set_traffic_lights(self, cycle_time=10):
        """
        Aggiunge automaticamente semafori alle strade in ingresso.
        Gestisce le fasi:
        - Gruppo Verticale (Nord/Sud): Fase 1 Verde, Fase 2 Rosso
        - Gruppo Orizzontale (Est/Ovest): Fase 1 Rosso, Fase 2 Verde
        """
        vertical_roads = []
        horizontal_roads = []

        for road in self.incoming_roads:
            # Calcoliamo l'angolo della strada (dagli ultimi due punti)
            p1 = road.points[-2]
            p2 = road.points[-1]
            angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
            
            # Se il seno è dominante, è verticale (angolo vicino a 90° o 270°)
            # Se il coseno è dominante, è orizzontale (angolo vicino a 0° o 180°)
            if abs(math.sin(angle)) > abs(math.cos(angle)):
                vertical_roads.append(road)
            else:
                horizontal_roads.append(road)

        # Creazione Semafori Verticali (Partono VERDI)
        for road in vertical_roads:
            self._add_light_to_road(road, cycle_time, "green")

        # Creazione Semafori Orizzontali (Partono ROSSI)
        for road in horizontal_roads:
            self._add_light_to_road(road, cycle_time, "red")

    def _add_light_to_road(self, road, cycle_time, initial_state):
        # Posizioniamo il semaforo 2 metri prima della fine della strada
        pos = road.get_length() - 2
        if pos < 0: pos = 0
        
        # Dobbiamo trovare l'indice numerico del segmento nella simulazione
        try:
            seg_index = self.sim.segments.index(road)
            self.sim.create_traffic_light(
                segment_id=seg_index,
                position=pos,
                cycle_time=cycle_time,
                initial_state=initial_state
            )
        except ValueError:
            print(f"Errore: La strada {road.id_segment} non è nella lista segmenti della simulazione.")