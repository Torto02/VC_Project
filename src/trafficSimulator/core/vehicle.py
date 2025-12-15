import uuid
import numpy as np

class Vehicle:
    def __init__(self, config={}):
        # Set default configuration
        self.set_default_config()

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)

        # Calculate properties
        self.init_properties()
        
    def set_default_config(self):    
        self.id = uuid.uuid4()

        # Proprietà Fisiche base
        self.l = 4          # Lunghezza
        self.w = 2          # Aggiungiamo la LARGHEZZA (width) per il disegno
        self.s0 = 4
        self.T = 1
        self.v_max = 16.6
        self.a_max = 1.44
        self.b_max = 4.61

        # Nuove Proprietà: Classe veicolo
        self.vehicle_class = "car"  # car, truck, bus, motorcycle

        # Nuove Proprietà: Dati OBU (On-Board Unit)
        self.engine_type = "combustion" # electric, hybrid
        self.co2_emissions = 0.0        # g/km istantaneo
        self.rpm = 0.0                  # Giri motore
        self.fog_lights = False
        self.rain_sensor = False

        self.path = []
        self.current_road_index = 0

        self.x = 0
        self.v = 0
        self.a = 0
        self.stopped = False
    def init_properties(self):
        self.sqrt_ab = 2*np.sqrt(self.a_max*self.b_max)
        self._v_max = self.v_max

    def update(self, lead, dt):
        # Update position and velocity
        if self.v + self.a*dt < 0:
            self.x -= 1/2*self.v*self.v/self.a
            self.v = 0
        else:
            self.v += self.a*dt
            self.x += self.v*dt + self.a*dt*dt/2
        
        # Update acceleration
        alpha = 0
        if lead:
            delta_x = lead.x - self.x - lead.l
            delta_v = self.v - lead.v

            alpha = (self.s0 + max(0, self.T*self.v + delta_v*self.v/self.sqrt_ab)) / delta_x

        self.a = self.a_max * (1-(self.v/self.v_max)**4 - alpha**2)

        if self.stopped: 
            self.a = -self.b_max*self.v/self.v_max
        
        if self.stopped: 
            self.a = -self.b_max*self.v/self.v_max
        
        # --- AGGIUNTA SIMULAZIONE OBU ---
        # Simulazione semplice RPM (proporzionale alla velocità + un minimo)
        # Supponiamo un rapporto fisso per semplicità
        if self.v > 0.1:
            self.rpm = 800 + (self.v * 150)  # Esempio: 800 rpm idle + incremento
        else:
            self.rpm = 800 # Idle

        # Simulazione CO2 (modello semplificato basato su velocità e accelerazione positiva)
        # Emissione base + sforzo motore
        if self.engine_type == "electric":
            self.co2_emissions = 0.0
        else:
            base_emission = 2.0 
            acceleration_factor = max(0, self.a) * 10
            speed_factor = self.v * 0.5
            self.co2_emissions = base_emission + acceleration_factor + speed_factor
        