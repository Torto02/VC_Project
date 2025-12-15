from trafficSimulator.core.obstacle import Obstacle
from trafficSimulator.core.static_object import StaticObject
from .vehicle_generator import VehicleGenerator
from .geometry.quadratic_curve import QuadraticCurve
from .geometry.cubic_curve import CubicCurve
from .geometry.segment import Segment
from .vehicle import Vehicle


class Simulation:
    def __init__(self):
        self.segments = []
        self.vehicles = {}
        self.vehicle_generator = []
        self.static_objects = [] 
        self.obstacles = []

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

    def create_quadratic_bezier_curve(self, start, control, end, **kwargs):
        cur = QuadraticCurve(start, control, end, **kwargs)
        self.add_segment(cur)

    def create_cubic_bezier_curve(self, start, control_1, control_2, end, **kwargs):
        cur = CubicCurve(start, control_1, control_2, end, **kwargs)
        self.add_segment(cur)

    def create_vehicle_generator(self, **kwargs):
        gen = VehicleGenerator(kwargs)
        self.add_vehicle_generator(gen)

    def create_static_object(self, x, y, width, height, color, shape="rectangle"):
        obj = StaticObject(x, y, width, height, color, shape)
        self.static_objects.append(obj)

    def create_obstacle(self, segment_id, position, duration):
        # segment_id è l'indice numerico del segmento nella lista self.segments
        obs = Obstacle(segment_id, position, duration)
        self.obstacles.append(obs)

    def run(self, steps):
        for _ in range(steps):
            self.update()

    # def update(self):
    #     # Update vehicles
    #     for segment in self.segments:
    #         if len(segment.vehicles) != 0:
    #             self.vehicles[segment.vehicles[0]].update(None, self.dt)
    #         for i in range(1, len(segment.vehicles)):
    #             self.vehicles[segment.vehicles[i]].update(self.vehicles[segment.vehicles[i-1]], self.dt)

    #     # Check roads for out of bounds vehicle
    #     for segment in self.segments:
    #         # If road has no vehicles, continue
    #         if len(segment.vehicles) == 0: continue
    #         # If not
    #         vehicle_id = segment.vehicles[0]
    #         vehicle = self.vehicles[vehicle_id]
    #         # If first vehicle is out of road bounds
    #         if vehicle.x >= segment.get_length():
    #             # If vehicle has a next road
    #             if vehicle.current_road_index + 1 < len(vehicle.path):
    #                 # Update current road to next road
    #                 vehicle.current_road_index += 1
    #                 # Add it to the next road
    #                 next_road_index = vehicle.path[vehicle.current_road_index]
    #                 self.segments[next_road_index].vehicles.append(vehicle_id)
    #             # Reset vehicle properties
    #             vehicle.x = 0
    #             # In all cases, remove it from its road
    #             segment.vehicles.popleft() 

    #     # Update vehicle generators
    #     for gen in self.vehicle_generator:
    #         gen.update(self)
    #     # Increment time
    #     self.t += self.dt
    #     self.frame_count += 1

    def update(self):
        # 1. Aggiorna e Rimuovi ostacoli scaduti
        for obs in self.obstacles:
            obs.update(self.dt)
        self.obstacles = [obs for obs in self.obstacles if obs.active]

        # 2. Aggiorna veicoli
        for segment_index, segment in enumerate(self.segments):
            # Troviamo gli ostacoli su QUESTO segmento
            obstacles_on_segment = [obs for obs in self.obstacles if obs.segment_id == segment_index]
            
            for i, vehicle_id in enumerate(segment.vehicles):
                vehicle = self.vehicles[vehicle_id]
                
                # Chi è il "lead" (davanti)?
                lead = None
                
                # A. Controlliamo se c'è un veicolo davanti
                if i > 0:
                    lead = self.vehicles[segment.vehicles[i-1]]
                
                # B. Controlliamo se c'è un ostacolo PIÙ VICINO del veicolo davanti
                # Cerchiamo ostacoli che sono davanti al veicolo (obs.x > vehicle.x)
                relevant_obstacles = [obs for obs in obstacles_on_segment if obs.x > vehicle.x]
                
                if relevant_obstacles:
                    # Troviamo l'ostacolo più vicino
                    closest_obs = min(relevant_obstacles, key=lambda o: o.x)
                    
                    # Se abbiamo già un veicolo davanti, vediamo chi è più vicino tra i due
                    if lead:
                        if closest_obs.x < lead.x:
                            lead = closest_obs # L'ostacolo è più vicino, diventa il target
                    else:
                        lead = closest_obs # Niente veicoli, solo l'ostacolo

                # Aggiorniamo il veicolo passandogli il target (veicolo o ostacolo)
                vehicle.update(lead, self.dt)

        # 3. Check veicoli fuori strada (codice esistente invariato)
        # ... (copia qui la parte del ciclo 'Check roads for out of bounds vehicle' dal vecchio codice) ...
        # ... (copia update vehicle generators e time increment) ...
        
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
