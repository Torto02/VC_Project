import json
from .simulation import Simulation

class ConfigLoader:
    def __init__(self):
        pass

    def load_from_file(self, file_path):
        with open(file_path, 'r') as f:
            config = json.load(f)
        return self.create_simulation_from_config(config), config

    def create_simulation_from_config(self, config):
        sim = Simulation()

        # 1. Carica i Segmenti Stradali
        for seg_conf in config.get("segments", []):
            # Estrae i punti (start, end) o curve
            seg_type = seg_conf.get("type", "line")
            
            # Argomenti comuni (category, max_speed)
            kwargs = {
                "category": seg_conf.get("category", "general"),
                "max_speed": seg_conf.get("max_speed", 50),
                "id_segment": seg_conf.get("id", None)
            }

            if seg_type == "line":
                p1 = tuple(seg_conf["start"])
                p2 = tuple(seg_conf["end"])
                sim.create_segment(p1, p2, **kwargs)
            
            elif seg_type == "quadratic":
                p1 = tuple(seg_conf["start"])
                control = tuple(seg_conf["control"])
                p2 = tuple(seg_conf["end"])
                sim.create_quadratic_bezier_curve(p1, control, p2, **kwargs)

        # 2. Carica i Generatori di Veicoli
        for gen_conf in config.get("vehicle_generators", []):
            rate = gen_conf.get("vehicle_rate", 10)
            vehicles = []
            for veh_conf in gen_conf.get("vehicles", []):
                weight = veh_conf[0]
                specs = veh_conf[1]
                # Assicuriamoci che specs abbia un path valido (usa indici numerici per ora)
                vehicles.append((weight, specs))
            
            sim.create_vehicle_generator(vehicle_rate=rate, vehicles=vehicles)

        # 3. Carica gli Oggetti Ambientali (Static Objects)
        for obj_conf in config.get("environment", []):
            sim.create_static_object(
                x=obj_conf["x"],
                y=obj_conf["y"],
                width=obj_conf["width"],
                height=obj_conf["height"],
                color=tuple(obj_conf["color"]),
                shape=obj_conf.get("shape", "rectangle")
            )

        return sim