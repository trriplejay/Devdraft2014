# pylint: disable=all
import sys


class StationGraph(object):
	"""
	A stationgraph allows a graph data structure to be built by
	passing in information one station at a time.  From the graph's
	perspective, each station would be considered a node in the graph.  The
	stationgraph is made of a nested dictionary arranged by stops rather than
	by trains.  Each stop will contain info about where the passenger can go
	next and how much it will cost.  This dictionary will then be used to
	determine the lowest cost path from start to D.  Since there is no limit
	on how many times a passenger can switch trains, that information will be
	eliminated when building the graph.
	"""

	def __init__(self, numLines, finalStop):

		self.final_stop = int(finalStop)
		self.num_train_lines = int(numLines)

		##station_graph is a nested dict organized as follows:
		### {station: {station: cost, station: cost, station: cost}}
		##initialize it to our final stop (which goes nowhere)
		self.station_graph ={int(self.final_stop):{}}


	def build_graph(self, key1, key2, value):
		#the graph will be a nested dictionary, so we need 2 keys to get
		#to a value.  The value will be the cost of traveling from
		#key1 to key2
		if not key1 in self.station_graph:
			self.station_graph[key1]={key2:value}
		elif not key2 in self.station_graph[key1]:
			self.station_graph[key1][key2]=value
		else:
			current = self.station_graph[key1][key2]
			if value < current:
				self.station_graph[key1][key2]=value


	def print_station_graph(self):
		for key1 in self.station_graph:
			print str(key1)+"->",
			for value in self.station_graph[key1]:
				print str(value)+':'+str(self.station_graph[key1][value])+",",
			print ""

	def shortest_path(self):
		"""
		Using Djikstra's shortest path algorithm, determine optimal costs
		from the start station to each subsequent station, then return the
		value of the cost to travel from the starting station to the
		ending station.
		Passengers always start at location 0, so that is set to be the
		source station.
		Since trains only move forward, from start (0) to end (numstops),
		the graph is treated as directed and acyclic, which is great because
		it allows the shortest path calculation to be done in linear time
		O(nodes + edges)
		"""
		#dict that will hold the cost of traveling to each station
		#add the initial cost of the starting station, which is 0
		D = {0:0}

		#add all of our dict keys (stations) to our queue
		station_queue = self.station_graph.keys()

		#sort the keys! since the graph is directed and acyclic, the stations
		#can be explored one at a time, in order, without having to adjust
		#for the lowest distance value via priority queue.
		#
		#sort them with reverse=True so that they can be popped from the
		#end of the list instead of from the beginning.  This should save
		#some cpu time.
		station_queue.sort(reverse=True)
		while len(station_queue) > 0:

			station = station_queue.pop() #grab the next node in the queue

			for next_st, next_cost in self.station_graph[station].iteritems():
				#loops through the current station's neighbors, and calculates
				#their costs from the starting node, making sure to store
				#the lowest cost in our D dict
				alt = D[station] + next_cost #sum the costs
				if not D.has_key(next_st) or alt < D[next_st]:
					#if there is no cost on record, or if the newly calculated
					#cost is lower than the currently recorded one, then
					#record the newly calculated cost as the lowest
					D[next_st] = alt #set the cost to get to next_st

		return D[self.final_stop]


if __name__ == '__main__':

	"""
	The traingraph is initialized from standard input as follows:
	first line is two integers separated by a space.
	first integer is represented by "K" in description
	but will be numLines here.
	The second integer is the position of the destination D which
	will be called finalStop here
	"""

	##instantiate our object to set up its internals
	numLines, finalStop = sys.stdin.readline().strip().split()
	tripPlanner = StationGraph(numLines, finalStop)

	"""
	The next few lines will be read in groups of 3,
	1st line is the number of stops for that train
	2nd line is list of stops
	3rd line is list of costs per stop
	"""
	for i in xrange (0,tripPlanner.num_train_lines):
		numstops = sys.stdin.readline().strip()
		stopline = sys.stdin.readline().strip().split()
		costline = sys.stdin.readline().strip().split()
        ##pass in each station, what it points to, and its travel cost
		for j in xrange(0, int(numstops)-1):
			#build the graph, one node at a time
			tripPlanner.build_graph(
				int(stopline[j]),
				int(stopline[j+1]),
				int(costline[j])
			)

	"""
	Now that the graph is built, call shortest_path to determine
	the lowest cost from beginning to end.
	"""
	print tripPlanner.shortest_path()
