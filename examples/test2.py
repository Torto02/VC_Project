import trafficSimulator as ts

loader = ts.ConfigLoader()
sim, config = loader.load_from_file('./examples/test_navigation.json')

win = ts.Window(sim)
win.run()
win.show()