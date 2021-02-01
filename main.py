from Network import Network
from helpers import helpers
import sys

topologyData = []
fileName = str(sys.argv[1])
rounds = int(sys.argv[2])

topologyData = helpers.readFile(fileName)
sim = Network(sys.argv[1], topologyData)
sim.createNodes()
sim.beginRounds(rounds)
sim.printResult()

# all tables coverged
with open ( 'outputfile.txt' , 'a' ) as outFile :
	outFile.write('\n\tPOST CONVERGENCE\t\n')
	outFile.write(sim.route)
	outFile.write(sim.returnRoutes())
