import trafficSimulator as ts

sim = ts.Simulation()

# Creiamo una strada lunga (Indice segmento: 0)
sim.create_segment((0, 0), (300, 0), category="general")

# Generatore di veicoli misti
sim.create_vehicle_generator(
    vehicle_rate=15,
    vehicles=[
        # Aggiunto 'path': [0] a tutti i veicoli
        
        # Peso 5: Auto normali
        (5, {'vehicle_class': 'car', 'path': [0], 'l': 4, 'w': 2, 'v_max': 20}),
        
        # Peso 2: Camion
        (2, {'vehicle_class': 'truck', 'path': [0], 'l': 8, 'w': 2.8, 'v_max': 12, 'engine_type': 'diesel'}),
        
        # Peso 1: Autobus
        (5, {'vehicle_class': 'bus', 'path': [0], 'l': 8, 'w': 2.5, 'v_max': 15}),
        
        # Peso 2: Moto
        (2, {'vehicle_class': 'motorcycle', 'path': [0], 'l': 2, 'w': 1, 'v_max': 25})
    ]
)

win = ts.Window(sim)
win.run()
win.show()