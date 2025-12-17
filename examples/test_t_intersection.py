import trafficSimulator as ts

sim = ts.Simulation()

# 1. Creiamo l'oggetto incrocio
inter = sim.create_intersection(0, 0, id_inter="T_Junction")

# 2. Creiamo le strade Esterne
# Strada da OVEST (Entrata) che si ferma all'incrocio (-10, 0)
west_in = sim.create_segment((-100, 0), (-10, 0), id_segment="west_in", category="general")

# Strada verso NORD (Uscita) che parte da (0, 10)
north_out = sim.create_segment((0, 10), (0, 100), id_segment="north_out", category="general")

# Strada verso SUD (Uscita) che parte da (0, -10)
south_out = sim.create_segment((0, -10), (0, -100), id_segment="south_out", category="general")

# 3. Registriamo le strade nell'incrocio e costruiamo
# Nota: create_segment non ritorna l'oggetto direttamente se non modifichiamo simulation.py
# Ma possiamo recuperarlo dall'ultima posizione o modificare create_segment per ritornarlo.
# (Assumiamo che tu abbia modificato simulation.py per far ritornare l'oggetto creato, 
#  oppure usiamo sim.segments[-1], sim.segments[-2]...)

# Recuperiamo gli oggetti (metodo sicuro basato sugli ultimi aggiunti)
# south_out è l'ultimo (-1), north_out è -2, west_in è -3
s_out_obj = sim.segments[-1]
n_out_obj = sim.segments[-2]
w_in_obj = sim.segments[-3]

inter.add_incoming(w_in_obj)
inter.add_outgoing(n_out_obj)
inter.add_outgoing(s_out_obj)

# Questo creerà Ovest->Nord (svolta sx) e Ovest->Sud (svolta dx)
inter.build()

# 4. Veicoli
sim.create_vehicle_generator(
    vehicle_rate=10,
    vehicles=[
        # Auto che vuole andare a Nord (svolta sinistra)
        (1, {'vehicle_class': 'car', 'start_road': 'west_in', 'end_road': 'north_out'}),
        # Auto che vuole andare a Sud (svolta destra)
        (1, {'vehicle_class': 'car', 'start_road': 'west_in', 'end_road': 'south_out'})
    ]
)

win = ts.Window(sim)
win.run()
win.show()