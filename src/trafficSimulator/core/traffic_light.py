class TrafficLight:
    def __init__(self, segment_id, position, cycle_time=5, initial_state="red"):
        self.segment_id = segment_id
        self.x = position       # Posizione in metri dall'inizio del segmento
        self.cycle_time = cycle_time # Tempo in secondi per cambiare stato
        self.state = initial_state   # "red" o "green"
        
        self.time_elapsed = 0

    def update(self, dt):
        self.time_elapsed += dt
        if self.time_elapsed >= self.cycle_time:
            self.time_elapsed = 0
            self.toggle_state()

    def toggle_state(self):
        if self.state == "red":
            self.state = "green"
        else:
            self.state = "red"

    @property
    def is_active(self):
        # Il semaforo è un "ostacolo attivo" solo se è ROSSO
        return self.state == "red"