import trafficSimulator as ts

sim = ts.Simulation()

# Strada dritta di 200m
sim.create_segment((0, 0), (200, 0), category="general")

# Generiamo veicoli (indice strada 0)
sim.create_vehicle_generator(
    vehicle_rate=15, 
    vehicles=[(1, {'vehicle_class': 'car', 'path': [0], 'v_max': 20})]
)

# --- CREIAMO UN INCIDENTE ---
# Sulla strada 0, a 150 metri dall'inizio, che dura 20 secondi
sim.create_obstacle(segment_id=0, position=150, duration=200)

win = ts.Window(sim)
win.run()
win.show()