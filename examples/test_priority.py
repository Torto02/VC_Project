import trafficSimulator as ts
import random

# Creiamo la simulazione
sim = ts.Simulation()

# ---------------------------------------------------------
# 1. TOPOLOGIA: Incrocio a 4 vie
# ---------------------------------------------------------
# Creiamo l'hub centrale
cross = sim.create_intersection(0, 0, id_inter="MainCross", size=15)

# Coordinate per le strade (Lunghe 80m)
# OVEST (Viale Principale)
w_in = sim.create_segment((-120, 0), (-7.5, 0), category="general", id_segment="west_in")
w_out = sim.create_segment((-7.5, 4), (-120, 4), category="general", id_segment="west_out")

# EST (Viale Principale)
e_in = sim.create_segment((120, 4), (7.5, 4), category="general", id_segment="east_in")
e_out = sim.create_segment((7.5, 0), (120, 0), category="general", id_segment="east_out")

# NORD (Strada Secondaria con STOP)
n_in = sim.create_segment((3, 120), (3, 7.5), category="general", id_segment="north_in")
n_out = sim.create_segment((0, 7.5), (0, 120), category="general", id_segment="north_out")

# SUD (Strada Secondaria con STOP)
s_in = sim.create_segment((0, -80), (0, -7.5), category="general", id_segment="south_in")
s_out = sim.create_segment((3, -7.5), (3, -80), category="general", id_segment="south_out")

# Colleghiamo le strade all'incrocio
cross.add_incoming(w_in)
cross.add_incoming(e_in)
cross.add_incoming(n_in)
cross.add_incoming(s_in)

cross.add_outgoing(w_out)
cross.add_outgoing(e_out)
cross.add_outgoing(n_out)
cross.add_outgoing(s_out)

# Costruiamo le corsie interne
cross.build()


# ---------------------------------------------------------
# 2. REGOLE DEL TRAFFICO
# ---------------------------------------------------------

# Aggiungiamo STOP alle strade secondarie (Nord e Sud)
cross.add_stop_sign(n_in)
cross.add_stop_sign(s_in)

# Calcoliamo automaticamente le priorità
# Risultato atteso:
# - Nord/Sud danno precedenza a TUTTI (perché hanno lo Stop)
# - Ovest/Est si danno precedenza a vicenda solo se svoltano a sinistra (traffico incrociato)
cross.calculate_priorities()


# ---------------------------------------------------------
# 3. TRAFFICO (VEICOLI)
# ---------------------------------------------------------

# A. FLUSSO PRINCIPALE (Est-Ovest) - Veloce e frequente
# Questi veicoli NON si fermeranno, costringendo gli altri ad aspettare
sim.create_vehicle_generator(
    vehicle_rate=5, # Tante auto
    vehicles=[
        (1, {'vehicle_class': 'car', 'start_road': 'west_in', 'end_road': 'east_out', 'v_max': 10})
    ]
)

# B. FLUSSO SECONDARIO (Nord-Sud) - Lento e cauto
# Questi veicoli incontreranno lo STOP
sim.create_vehicle_generator(
    vehicle_rate=1, # Meno auto
    vehicles=[
        # Camion da Nord che deve andare a Sud
        (1, {'vehicle_class': 'truck', 'start_road': 'north_in', 'end_road': 'south_out', 'v_max': 10}),
        # Auto da Sud che deve andare a Nord
    ]
)

sim.create_vehicle_generator(
    vehicle_rate=10, # Meno auto
    vehicles=[
        # Camion da Nord che deve andare a Sud
        # Auto da Sud che deve andare a Nord        
        # Qualcuno che svolta (dallo Stop deve aspettare comunque)
        (1, {'vehicle_class': 'bus', 'start_road': 'south_in', 'end_road': 'east_out', 'v_max': 8})
    ]
)

# ---------------------------------------------------------
# 4. AVVIO
# ---------------------------------------------------------
win = ts.Window(sim)
win.zoom = 5 # Zoomiamo un po' indietro per vedere tutto
win.run()
win.show()