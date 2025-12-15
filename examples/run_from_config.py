import trafficSimulator as ts

# Crea il loader
loader = ts.ConfigLoader()

# Carica simulazione e config dal JSON
sim, config = loader.load_from_file('./examples/my_config.json')

# Avvia la finestra
win = ts.Window(sim)

# (Opzionale) Qui potremmo impostare il titolo della finestra usando config['window']
# ma richiede modifiche a Window.setup() che al momento ha valori hardcoded.
# Per ora, godiamoci la simulazione popolata.

win.run()
win.show()