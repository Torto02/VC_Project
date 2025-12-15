from trafficSimulator import *
sim = Simulation()


# Strada normale
sim.create_segment((0, 0), (100, 0), category="general")

# Corsia preferenziale Bus (sarà rossa)
sim.create_segment((0, 5), (100, 5), category="bus")

# Strada sterrata (sarà marrone)
sim.create_segment((0, 10), (100, 10), category="dirt")

win = Window(sim)
win.run()
win.show()