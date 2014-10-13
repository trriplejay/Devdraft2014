# your code goes here
# pylint: disable=all
import sys


class Train(object):
	"""
	A train is a simple class containing a dictionary of stop:cost pairs, and
	an integer value of its total number of stops.
	Not useful for first challenge, but may be needed later.
	"""
	def __init__(self, numstops, stoplist, costlist):
		self.totalstops=int(numstops)
		self.stops_dict={}
		if len(stoplist) <= len(costlist):
				print "bad input, can't have more costs than stops"
		else:
			for x in range(0,len(costlist)):
				self.stops_dict[stoplist[x]]=costlist[x]

	def printMyDict(self):
		print self.stops_dict


class StationGraph(object):
	"""
	A traingraph is made up of multiple trains, each which contains information
	about its own stops and costs.  From a graph standpoint, each stop will
	be considered a node.  The traingraph object will start as a list of
	trains, and will build a nested dictionary arranged by stops rather than
	by trains.  Each stop will contain info about which trains have costs
	associated with that stop.  This dictionary will then be used to determine
	the lowest cost path from start to D
	"""

	def __init__(self):

		"""
		The traingraph is initialized from standard input as follows:
		first line is two integers separated by a space.
		first integer is represented by "K" in description
		but will be num_train_lines here.
		second integer is the position of the destination D
		will be final_stop here
		"""
		self.num_train_lines, self.final_stop = sys.stdin.readline().split()
		self.final_stop = int(self.final_stop)

		## train_list is a nested dict organized as follows:
		### {train : {station: cost, station: cost, station: cost}}
		self.train_list = []
		##station_graph is a nested dict organized as follows:
		### {station: {station: cost, station: cost, station: cost}}
		##initialize it to our final stop (which goes nowhere)
		self.station_graph ={int(self.final_stop):{}}


		"""
		The next few lines will be read in groups of 3,
		1st line is the number of stops for that train
		2nd line is list of stops
		3rd line is list of costs per stop
		"""
		for i in xrange (0,int(self.num_train_lines)):
			numstops = sys.stdin.readline()
			stopline = sys.stdin.readline().split()
			costline = sys.stdin.readline().split()
            ##pass in each node, what it points to, and its travel cost
			for j in xrange(0, int(numstops)-1):
				self.build_graph(
					int(stopline[j]),
					int(stopline[j+1]),
					int(costline[j])
				)

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


	def print_trains(self):
		print "here is the train list contained in our graph object: "
		for train in self.train_list:
			print "here's a train: "
			train.printMyDict()

	def shortest_path(self):
		"""
		Using Djikstra's shortest path algorithm, determine
		optimal distances from the start node to each subsequent node,
		then return the value of the cost to travel from the start node to the
		end node.
		I assume that the train always starts at station "0" since that
		is how all of the examples are organized and nothing indicates
		otherwise
		"""
		start={0:0}
		end=self.final_stop #based on stdin value
		graph = self.station_graph
		D = {0:0} #dict that will hold the cost of traveling to each node
		P = {} #a list of nodes visited, in case we want to trace the path

		node_queue = graph.keys()
		while len(node_queue) > 0:
			shortest = None
			node = node_queue[0]

			for temp_node in node_queue[1:]: #skip our initial location
				"""
				if we havent logged a cost for the node, or if we have but
				temp_node is better, set node to temp_node
				"""
				if (not D.has_key(node)) or (D.has_key(temp_node) and D[temp_node] < D[node]):
					node = temp_node

			node_queue.remove(node)

			for child_node, child_value in graph[node].iteritems():
				"""
				loop through our current node's children, and look at
				their values
				"""
				if child_node in node_queue:
					alt = D[node] + child_value #sum the costs
					if not D.has_key(child_node) or alt < D[child_node]:
						D[child_node] = alt #set the cost to get to child_node
						P[child_node] = node #set the path


		return D[end]


if __name__ == '__main__':

	##instantiate our object to set up its internals
	x = StationGraph()

	"""
	during init, the graph was built.  Now we can call shortest_path to
	learn out the lowest cost
	"""
	print x.shortest_path()
