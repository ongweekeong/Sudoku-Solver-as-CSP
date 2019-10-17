import sys
import copy
import queue

rows = "ABCDEFGHI"
cols = "123456789"

def add(x, y):

	return [xi+yi for xi in x for yi in y]

squares = [row+col for row in rows for col in cols] # Names the squares from A1...to...I9
groups = ([add(row, cols) for row in rows] +
		 [add(rows, col) for col in cols] +
		 [add(r, c) for r in ("ABC", "DEF", "GHI") for c in ("123", "456", "789")]) # All 27 groups of 9 variables for the 27 AllDiff constraints
square_in_groups = dict((x, [y for y in groups if x in y]) for x in squares) # Dictionary (x:y) : x is the variable, y is a list of the 3 groups that the variable belongs to   	

class Sudoku(object):
	def __init__(self, puzzle):
		# you may add more attributes if you need
		self.puzzle = puzzle # self.puzzle is a list of lists
		self.variables = squares
		#self.values = dict.fromkeys(squares)
		self.neighbours = self.get_neighbours()
		self.domains = self.get_domains()
		self.constraints = set((x, y) for x in squares for y in self.neighbours[x])
		self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists

	def solve(self):
		#TODO: Your code here
		self.AC3()
		assignment = self.get_assignment()
		solved_puzzle = self.backtracking_search(assignment)
		self.get_solution(solved_puzzle)

		# don't print anything here. just return the answer
		# self.ans is a list of lists
		return self.ans

	def get_neighbours(self):
		neighbours = dict((x, set()) for x in squares)

		for variable in squares:
			for groups in square_in_groups[variable]:
				for y in groups:
					if y != variable:
						neighbours[variable].add(y)

		return neighbours	

	def get_domains(self):
		domains = dict((x, []) for x in squares)

		# transfers puzzle into domain
		i, j = 0, 0
		for variable in squares:
			if self.puzzle[i][j] != 0:
				domains[variable].append(puzzle[i][j])
				#self.values[variable] = puzzle[i][j]
			else:
				domains[variable].extend([1,2,3,4,5,6,7,8,9])

			j = j + 1	
			if j == 9:
				i = i + 1
				j = 0

		return domains	

	# Get the starting assignments from the starting puzzle
	def get_assignment(self):	
		assignment = {}

		for variable in self.domains:
			if len(self.domains[variable]) == 1:
				assignment[variable] = self.domains[variable][0]

		return assignment

	def AC3(self):
		q = queue.Queue()

		for constraint in self.constraints:
			q.put(constraint)

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
 
		domain = copy.deepcopy(self.domains)    

		var = self.select_variable(assignment)

		if var in self.domains:	
			for assigning_value in self.domains[var]:
				if self.isConsistent(var, assigning_value, assignment):
					assignment[var] = assigning_value
					check = self.forward_checking(domain, var, assigning_value, assignment) 

					if check != {"FAILURE"}:
						result = self.backtrack(assignment) # Calls backtrack again for the next variable assignment
						if result != {"FAILURE"}:
							return result

					del assignment[var]
					self.domains.update(domain)	

		return {"FAILURE" : "FAILURE"}            

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

	# Uses minimum remaining values heuristic
	def select_variable(self, assignment):
		min_variables = dict({x, len(self.domains[x])} for x in squares if x not in assignment)

		min_var = min(min_variables, key=min_variables.get)
		
		return min_var		

	# Maintaining arc consistency
	def forward_checking(self, domain, var, value, assignment):

		q = queue.Queue()

		for neighbour in self.neighbours[var]:
			if neighbour not in assignment and value in domain[neighbour]:
				domain[neighbour].remove(value) # Might have problems with this

			if not domain[neighbour]: # when domain neighbour becomes empty
				return {"FAILURE"}

			if len(domain[neighbour]) == 1:
				neighbour_value = domain[neighbour][0]
				q.put(neighbour)

				for check_neighbour in self.neighbours[neighbour]:
					if check_neighbour not in assignment and neighbour_value in domain[check_neighbour]:
						domain[check_neighbour].remove(neighbour_value)

					if not domain[check_neighbour]:
						return {"FAILURE"}	
				
		"""while not q.empty():
			forward_check = q.get()
			check_var = forward_check[0]
			check_value = domain[forward_check]

			for neighbour in self.neighbours[check]:
				if neighbour not in assignment and value in domain[neighbour]:
					domain[neighbour].remove(value)

				if not domain[neighbour]: # when domain neighbour becomes empty
					return {"FAILURE"}

				if len(domain[neighbour]) == 1:
					q.put(neighbour)

					for check_neighbour in self.neighbours[neighbour]:
						q.put((neighbour))"""

		return domain

	# copy ans from backtrack into self.puzzle

	def get_solution(self, solved_puzzle):

		i, j = 0, 0
		for variable in squares:
			self.puzzle[i][j] = solved_puzzle[variable]

			j = j + 1   
			if j == 9:
				i = i + 1
				j = 0

		return solved_puzzle

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
