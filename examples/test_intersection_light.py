import trafficSimulator as ts

sim = ts.Simulation()

# 1. Creiamo l'Incrocio
inter = sim.create_intersection(0, 0, id_inter="T_Lights", size=15)

# 2. Strade
# Ovest In (Orizzontale)
w_in = sim.create_segment((-100, 0), (-7.5, 0), category="general", id_segment="win")
# Sud In (Verticale)
s_in = sim.create_segment((0, -100), (0, -7.5), category="general", id_segment="sin")

# Uscita Nord e Est
n_out = sim.create_segment((0, 7.5), (0, 100), category="general", id_segment="nout")
e_out = sim.create_segment((7.5, 0), (100, 0), category="general", id_segment="eout")

# 3. Colleghiamo e Costruiamo
inter.add_incoming(w_in)
inter.add_incoming(s_in)
inter.add_outgoing(n_out)
inter.add_outgoing(e_out)
inter.build()

# 4. ATTIVIAMO I SEMAFORI (Ciclo 5 secondi)
# Questo metterà automaticamente:
# - Sud In (Verticale): VERDE iniziale
# - Ovest In (Orizzontale): ROSSO iniziale
inter.set_traffic_lights(cycle_time=5)

# 5. Veicoli
sim.create_vehicle_generator(
    vehicle_rate=20,
    vehicles=[
        # Auto da Ovest (incontrerà il ROSSO all'inizio)
        (1, {'vehicle_class': 'car', 'start_road': 'win', 'end_road': 'eout', 'v_max':15}),
        # Auto da Sud (incontrerà il VERDE all'inizio)
        (1, {'vehicle_class': 'bus', 'start_road': 'sin', 'end_road': 'nout', 'v_max':10})
    ]
)

win = ts.Window(sim)
win.run()
win.show()