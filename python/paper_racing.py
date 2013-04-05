class Team:
	def __init__(self,name):
		self.name = name
		self.boats = []
	def add_boat(self,boat):
		if boat not in self.boats:
			self.boats.append(boat)
	def __str__(self):
		return self.name

class Boat:
	def __init__(self,name,team):
		self.name = name
		self.team = team
		self.team.add_boat(self)
	def __str__(self):
		return str(self.team) + " " + str(self.name)

class Race:
	def __init__(self):
		self.results = []
	def add_result(self,result):
		self.results.append(result)
	def __str__(self):
		out = ""
		for r in self.results:
			out = out + str(r) + "\n"
		return out

class Result:
	def __init__(self,boat,time):
		self.boat = boat
		self.time = time
	def __str__(self):
		return str(self.boat) + ": " + str(self.time)
	def time(self):
		return self.time.seconds

class Time:
	def __init__(self,timestring):
		self.timestring = timestring
		if ":" in timestring:
			words = timestring.split(":")
			self.seconds = 60*float(words[0]) + float(words[1])
	def __str__(self):
		return str(self.seconds) + " seconds"

class Graph:
	def __init__(self):
		self.nodes = []
		self.edges = []
	def add_node(self,node):
		if node not in self.nodes:
			self.nodes.append(node)
	def add_edge(self,edge):
		self.add_node(edge.u)
		self.add_node(edge.v)
		if edge not in self.edges:
			self.edges.append(edge)
	def adjacent(self,node):
		dist = dict()
		for e in self.edges:
			if e.u == node:
				dist[e.v] = e.weight
			elif e.v == node:
				dist[e.u] = -1.0*e.weight
		return dist
	def get_node_by_obj(self,obj):
		for node in self.nodes:
			if node.obj == obj:
				return node
	def get_distance(self,boat1,boat2):
		# implements Dijkstra algorithm to find distance between two boats
		dist = dict()
		unk = []
		for node in self.nodes:
			dist[node] = 10000
			unk.append(node)
		dist[self.get_node_by_obj(boat1)] = 0
		while len(unk) > 0:
			lowestcost = None
			for node in unk:
				if lowestcost == None or dist[node] < dist[lowestcost]:
					lowestcost = node
			unk.remove(lowestcost)
			adj = self.adjacent(lowestcost)
			adjnodes = adj.keys()
			for node in adjnodes:
				if dist[lowestcost] + adj[node] < dist[node]:
					dist[node] = dist[lowestcost] + adj[node]

		return dist[self.get_node_by_obj(boat2)]

class Node:
	def __init__(self,obj):
		self.obj = obj

class Edge:
	def __init__(self,u,v,weight):
		self.u = u
		self.v = v
		self.weight = float(weight)

boats = []
teams = []
races = []
results = []
times = []

# Helper method for finding a boat given the string of its team
# and its name.
def find_boat(team,boat):
	for b in boats:
		if b.name == boat and b.team.name == team:
			return b

# Reads in the text file information and populates the 
# boats, teams, races, results, times arrays.
def read_files():
	# Teams
	teamfile = open("../teams.txt","r")
	for line in teamfile:
		l = line.rstrip()
		t = Team(l)
		teams.append(t)

	# Boats
	boatfile = open("../boats.txt","r")
	curteam = None
	for line in boatfile:
		# Figure out what team
		if line.startswith("TEAM"):
			teamstring = line[5:].rstrip()
			for t in teams:
				if teamstring == t.name:
					curteam = t
		elif line.startswith("BOAT"):
			b = Boat(line[5:].rstrip(),curteam)
			boats.append(b)
		else:
			continue

	# Races
	racefile = open("../races.txt","r")
	currace = None
	for line in racefile:
		if line.startswith("RACE"):
			currace = Race()
			races.append(currace)
		elif line.startswith("RESULT"):
			resultstring = line[7:].rstrip()
			words = resultstring.split(',')
			b = find_boat(words[0],words[1])
			t = Time(words[2])
			r = Result(b,t)
			currace.add_result(r)
			results.append(r)
			times.append(t)
		else:
			continue

def build_graph():
	# Create the Graph
	graph = Graph()
	# Adding the nodes is easy
	for boat in boats:
		n = Node(boat)
		graph.add_node(n)
	# Now we add the edges. There exists an edge between boats u,v
	# iff there exists a race such that there is a result for 
	# both boat u and boat v. The weight of the edge is the time difference
	# between u,v (u.time - v.time). Self edges are not allowed.
	for race in races:
		for result1 in race.results:
			for result2 in race.results:
				if result1 == result2:
					continue
				else:
					boat1 = result1.boat
					node1 = graph.get_node_by_obj(boat1)
					time1 = result1.time.seconds

					boat2 = result2.boat
					node2 = graph.get_node_by_obj(boat2)
					time2 = result2.time.seconds

					weight = time1 - time2
					e = Edge(node1,node2,weight)
					graph.add_edge(e)
	return graph

def run_app():
	print "Welcome to Paper Racing!"
	while True:
		print "Enter boat 1 (e.g., MIT 1V):"
		boat1 = raw_input()
		words = boat1.split(" ")
		boat1 = find_boat(words[0] + " Lightweight Men",words[1])
		print "Enter boat 2:"
		boat2 = raw_input()
		words = boat2.split(" ")
		boat2 = find_boat(words[0] + " Lightweight Men",words[1])

		dist = graph.get_distance(boat1,boat2)
		if dist == 10000:
			print "These boats could not be compared."
		elif dist < 0:
			print "We predict " + str(boat1) + " winning by " + str(abs(dist)) + " seconds."
		elif dist > 0:
			print "We predict " + str(boat1) + " losing by " + str(abs(dist)) + " seconds."
		else:
			print "We predict a dead tie between these boats."

		print ""
		print "Would you like to compare more boats?"
		ans = raw_input()
		if ans != "y" and ans != "yes":
			break
	print "Thanks for using Paper Racing!"

# Main method:
read_files()
graph = build_graph()
run_app()
print "Press ENTER to quit."
raw_input()