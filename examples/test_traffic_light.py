import trafficSimulator as ts

sim = ts.Simulation()

# Strada lunga
sim.create_segment((0, 0), (200, 0), category="general")

# Traffico intenso per vedere la coda
sim.create_vehicle_generator(
    vehicle_rate=30, 
    vehicles=[(1, {'vehicle_class': 'car', 'path': [0], 'v_max': 20})]
)

# --- CREIAMO UN SEMAFORO ---
# Posizione 100 metri, ciclo di 4 secondi (4s Rosso / 4s Verde)
sim.create_traffic_light(segment_id=0, position=100, cycle_time=6)

win = ts.Window(sim)
win.run()
win.show()