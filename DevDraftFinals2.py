# pylint: disable=all
import sys


class StationNode(object):
	"""
	I played around on paper with a few solutions, but couldn't come up
	with anything that didn't have a ridiculous increase in time complexity.
	Ended up running out of time to get something working. Considered building
	some kind of tree structure, where each node is a station, and has a child
	for each station it connects to, each child then would represent a
	different train.  Each node could then keep track of the cost to get to
	that node based	on the path followed up to that point.  When limiting
	switches, I could just choose a child based on a combination of the cost
	and my switch limit.
	"""
	def __init__(self):
		#one child for each station that this station could take a passenger
		#to, which is a maximum of K (the number of trains)
		self.children=[]
		self.cost=0


class Train(object):
	"""
	A train is a simple class containing a dictionary of stop:cost pairs, and
	an integer value of its total number of stops.
	Not useful for first challenge, but may be needed later.
	"""
	def __init__(self, numstops, stoplist, costlist, solocost):
		self.totalstops=int(numstops)
		self.stops_dict={}
		self.solo_cost = solocost
		if len(stoplist) <= len(costlist):
				print "bad input, can't have more costs than stops"
		else:
			for x in range(0,len(costlist)):
				self.stops_dict[int(stoplist[x])]=int(costlist[x])

	def printMyDict(self):
		print self.stops_dict

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

	def __init__(self, numLines, finalStop, switchLimit):

		self.final_stop = int(finalStop)
		self.num_train_lines = int(numLines)
		self.switch_limit = int(switchLimit)
		self.num_switches = 0

		self.switching_points = []
		##station_graph is a nested dict organized as follows:
		### {station: {station: cost, station: cost, station: cost} }
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
			self.switching_points.append(key1)


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
		P = {} #a list of nodes visited, in case we want to trace the path

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
					P[next_st] = station

		S = list()

		while P.has_key(station):
			S.insert(0,P[station])
#			print "station is: ",
#			print station
#			print "my switching points: ",
#			print self.switching_points
#			if station in self.switching_points:
#				self.num_switches = self.num_switches + 1
			station = P[station]
#		print "my switching points: ",
#		print self.switching_points
#		print "number of switches taken: ",
#		print self.num_switches
		return D[self.final_stop]

	def shortest_x_paths(self, k=2):
		"""
		find k shortest paths using djikstra, and
		pick the one that contains a number of switches
		less than the defined limit
		"""
		A[0] = self.shortest_path()


if __name__ == '__main__':

	"""
	The stationgraph is initialized from standard input as follows:
	first line is three integers separated by a space.
	first integer is represented by "K" in description
	but will be numLines here.
	The second integer is the position of the destination D which
	will be called finalStop here
	The third integer is the maximum number of train switches allowed
	which here will be called switchLimit
	"""

	##instantiate our object to set up its internals
	numLines, finalStop, switchLimit = sys.stdin.readline().strip().split()
	tripPlanner = StationGraph(numLines, finalStop, switchLimit)

	"""
	The next few lines will be read in groups of 3,
	1st line is the number of stops for that train
	2nd line is list of stops
	3rd line is list of costs per stop
	"""
	myTrains = list()
	for i in xrange (0,tripPlanner.num_train_lines):
		numstops = sys.stdin.readline().strip()
		stopline = sys.stdin.readline().strip().split()
		costline = sys.stdin.readline().strip().split()
        ##pass in each station, what it points to, and its travel cost
		costsum = 0

		for j in xrange(0, int(numstops)-1):
			#build the graph, one node at a time
			costsum = costsum + int(costline[j])
			tripPlanner.build_graph(
				int(stopline[j]),
				int(stopline[j+1]),
				int(costline[j])
			)
		#__init__(self, numstops, stoplist, costlist, solocost):
		myTrains.append(Train(numstops, stopline, costline, costsum))


	"""
	Now that the graph is built, call shortest_path to determine
	the lowest cost from beginning to end.
	"""
	print tripPlanner.shortest_path()
#	for train in myTrains:
#		train.printMyDict()
#		print "solo cost: ",
#		print train.solo_cost
