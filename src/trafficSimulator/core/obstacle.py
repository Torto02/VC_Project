class Obstacle:
    def __init__(self, segment_id, position, duration, width=2, color=(255, 0, 0)):
        self.segment_id = segment_id
        self.x = position       # Distanza dall'inizio del segmento (metri)
        self.duration = duration # Durata in secondi
        self.width = width
        self.color = color
        
        # Proprietà per renderlo compatibile con la logica dei veicoli (IDM)
        self.v = 0              # Velocità: 0 m/s (è fermo!)
        self.l = 2              # Lunghezza occupata (metri)
        
        self.time_elapsed = 0
        self.active = True

    def update(self, dt):
        self.time_elapsed += dt
        if self.time_elapsed >= self.duration:
            self.active = False