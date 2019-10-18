import sys
import copy
import Queue
import time
start_time = time.time()
rows = "ABCDEFGHI"
cols = "123456789"

def add(x, y):

	return [xi+yi for xi in x for yi in y]

def get_row(var):
	return {
		'A': 0,
		'B': 1,
		'C': 2,
		'D': 3,
		'E': 4,
		'F': 5,
		'G': 6,
		'H': 7,
		'I': 8
		}[var[0]]

def get_col(var):
	return {
		'1': 0,
		'2': 1,
		'3': 2,
		'4': 3,
		'5': 4,
		'6': 5,
		'7': 6,
		'8': 7,
		'9': 8
		}[var[1]]		

squares = [row+col for row in rows for col in cols] # Names the squares from A1...to...I9
groups = ([add(row, cols) for row in rows] +
		 [add(rows, col) for col in cols] +
		 [add(row, col) for row in ("ABC", "DEF", "GHI") for col in ("123", "456", "789")]) # All 27 groups of 9 variables for the 27 AllDiff constraints
square_in_groups = dict((x, [y for y in groups if x in y]) for x in squares) # Dictionary (x:y) : x is the variable, y is a list of the 3 groups that the variable belongs to   	

class Sudoku(object):
	def __init__(self, puzzle):
		# you may add more attributes if you need
		self.puzzle = puzzle # self.puzzle is a list of lists
		self.variables = squares
		self.neighbours = self.get_neighbours()
		self.domains = self.get_domains()
		self.constraints = set((x, y) for x in squares for y in self.neighbours[x])
		self.ans = copy.copy(puzzle) # self.ans is a list of lists

	def solve(self):
		self.AC3() # Preprocessing
		solved_puzzle = self.backtracking_search({})

		# self.ans is a list of lists
		return self.ans

	# Returns a dictionary of a permanent list of neighbours for each variable
	def get_neighbours(self):
		neighbours = dict((x, set()) for x in squares)

		for variable in squares:
			for groups in square_in_groups[variable]:
				for y in groups:
					if y != variable:
						neighbours[variable].add(y)

		return neighbours	

	# Computes the domain of each variable from the initial state of the puzzle
	def get_domains(self):
		domains = dict((x, []) for x in squares)

		# transfers puzzle into domain
		i, j = 0, 0
		for variable in squares:
			if self.puzzle[i][j] != 0:
				domains[variable].append(puzzle[i][j])
			else:
				domains[variable].extend([1,2,3,4,5,6,7,8,9])

			j = j + 1	
			if j == 9:
				i = i + 1
				j = 0

		return domains	

	# Preprocessing step to reduce search space. Time complexity: O(n^2*d^3)
	def AC3(self):
		q = Queue.Queue()
		
		for var in squares:
			if self.puzzle[get_row(var)][get_col(var)] > 0:
				for constraint in self.constraints:
					if var == constraint[0]:
						q.put(constraint)
		#for constraint in self.constraints:
		#	q.put(constraint)

		while not q.empty():
			x = q.get()
			
			if self.revise(x[0], x[1]):
				if not self.domains[x[0]]:
					return False

				for neighbour in (self.neighbours[x[0]] - set(x[1])):
					q.put((neighbour, x[0]))

		return True

	def revise(self, xi, xj):	
		revised = False

		for value in self.domains[xi]:
			if not self.is_consistent(value, xi, xj):
				self.domains[xi].remove(value)
				revised = True

		return revised		 
	
	# Checks if x satisfies the constraint (xi, xj) for some values of xj ; Used in revise				
	def is_consistent(self, x, xi, xj):

		for value in self.domains[xj]:
			if xi in self.neighbours[xj] and x != value:
				return True

		return False		

	def backtracking_search(self, assignment):

		return self.backtrack(assignment)

	def backtrack(self, assignment):
		if self.is_complete(assignment):
			return assignment
 		
 		# Keeps the current copy of domain to be used for a backtrack in the future
		domain = copy.deepcopy(self.domains)    

		var = self.select_variable(assignment)

		if var in self.domains:	
			for value in self.domains[var]:
				if self.isConsistent(var, value, assignment):
					assignment[var] = value
					check = self.forward_checking(var, value, assignment) 

					if check:
						result = self.backtrack(assignment) # Calls backtrack again for the next variable assignment
						if len(result) != 0:
							self.puzzle[get_row(var)][get_col(var)] = value
							return result

					del assignment[var]
					self.domains.update(domain)	# Wrong assignment. Returning domains to previous values before the current assignment

		return {}

	# Checks if we have a complete assignment that is consistent
	def is_complete(self, assignment):

		if len(assignment) == 81:
			return True
		else:
			return False

	# Checks if any variable xj in the same group as this variable xi has already been assigned value
	def isConsistent(self, var, value, assignment):
		for neighbour in self.neighbours[var]:
			if neighbour in assignment and assignment[neighbour] == value:
				return False

		return True        

	# Uses minimum remaining values heuristic to select the next variable to be assigned
	def select_variable(self, assignment):
		min_variables = dict((x, len(self.domains[x])) for x in squares if x not in assignment)
		min_var = min(min_variables, key=min_variables.get)
		
		return min_var		

	# Does forward checking to see if the current assignment (of value to var) results in failure by checking if there are still values to be assigned
	# to the neighbours of var, and to the neighbours of the neighbours of var (somewhat between Forward Checking and Maintaining Arc Consistency) 
	def forward_checking(self, var, value, assignment):
		for neighbour in self.neighbours[var]:
			if neighbour not in assignment and value in self.domains[neighbour]:
				self.domains[neighbour].remove(value) 

			if not self.domains[neighbour]: # when domain of neighbour becomes empty
				return False
				#return {"FAILURE"}

			if len(self.domains[neighbour]) == 1:
				neighbour_value = self.domains[neighbour][0]
			
				for check_neighbour in self.neighbours[neighbour]:
					if check_neighbour not in assignment and neighbour_value in self.domains[check_neighbour]:
						self.domains[check_neighbour].remove(neighbour_value)

					if not self.domains[check_neighbour]:
						return False
					#	return {"FAILURE"}	

		return True

	# you may add more classes/functions if you think is useful
	# However, ensure all the classes/functions are in this file ONLY

if __name__ == "__main__":
	# STRICTLY do NOT modify the code in the main function here
	if len(sys.argv) != 3:
		print ("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
		raise ValueError("Wrong number of arguments!")

	try:
		f = open(sys.argv[1], 'r')
	except IOError:
		print ("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
		raise IOError("Input file not found!")

	puzzle = [[0 for i in range(9)] for j in range(9)]
	lines = f.readlines()

	i, j = 0, 0
	for line in lines:
		for number in line:
			if '0' <= number <= '9':
				puzzle[i][j] = int(number)
				j += 1
				if j == 9:
					i += 1
					j = 0

	sudoku = Sudoku(puzzle)
	ans = sudoku.solve()
	
	with open(sys.argv[2], 'a') as f:
		for i in range(9):
			for j in range(9):
				f.write(str(ans[i][j]) + " ")
			f.write("\n")
	
	print("--- %s seconds ---" % (time.time() - start_time)) # measures time taken to execute code