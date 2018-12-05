#! /usr/bin/python

# Written by Larry Montgomery
# cs480 Assignment 1
# functions:
# DFS, BFS , Heuristic based search

# notes on what objects are needed
# Agent, SearchTreeGenerator, Tree
#
#

# imports go below here
import sys
import queue as Q
import hashlib
from collections import deque

#
#
#
class node():
	
	#
	#
	#
	def __init__(self, parent, currState):
		self.parent = parent
		self.state = currState
		self.child_list = []
	#
	#
	#
	def addChild(self, parent, childValue):
		parent.child_list.append(childValue)
#
#
#
class Agent():
	#
	#
	#
	def __init__(self, inital_word, goal_word):
		self.inital_state = node('NONE',inital_word)
		self.goal_state = goal_word
		self.current_state = node('NONE',inital_word)
		self.known_states = [self.inital_state]
		self.valid_dict = []
		self.path = [inital_word]
		self.words_added = 0
	#
	#
	#
	def pick_successor(self, node_list):
		self.current_state = node_list.pop()
		self.path.append(self.current_state)
	#
	#
	#
	def update_path(self, word):
		self.path.append(word)
	#
	#
	#
	def generate_children(self, node_word):
		letter_list = node_word
		c_list = []
		pos = 0
		for letter in letter_list:
			pos += 1 
			for i in range(1,26):
				if ord(letter) + i <= 122:
					if pos == 1:
						child = chr( ord(letter) + i ) + letter_list[pos:]
					elif pos <= len(letter_list):
						child = letter_list[0:(pos - 1)] + chr( ord(letter) + i ) + letter_list[pos:]
				else:
					if pos == 1:
						child = chr( 96 + ((ord(letter) + i) - 122 )) + letter_list[pos:]
					elif pos <= len(letter_list):
						child = letter_list[0:(pos - 1)] + chr( 96 + ((ord(letter) + i) - 122 )) + letter_list[pos:]
				c_list.append(child)
		valid_child = self.validate_children(c_list)
		return valid_child
	#	valid_known_states = self.validate_known_states(valid_child, node_word)

	#	return valid_known_states
	
	#
	#
	#
	def validate_children(self, node_child_list):
		child_in_dict = []

		for child in node_child_list:
			for word in self.valid_dict:
				if child == word:
					child_in_dict.append(child)
				else:
					continue
		return child_in_dict
	#
	#
	#
	def validate_known_states(self, valid_child_list, parent_word):
		child_not_known = []
		known_states = []
		for i in self.known_states:
			known_states.append(i.state)
		for child in valid_child_list:
			if child not in known_states:
				child_not_known.append(child)
				self.known_states.append(node(parent_word,child))
		return child_not_known
	#
	#
	#
	def create_dictionary(self):
		curr_dict = open('words.txt','r')
		for word in curr_dict:
			word = word.rstrip('\n')
			if len(word) == len(self.inital_state.state):
				self.valid_dict.append(word)
	#
	#
	#
	def BFS(self):
		curr_search_level = self.generate_children(self.current_state.state)

		child_curr_level = []
		while self.current_state.state != self.goal_state:
			for word in curr_search_level:
				if word == self.goal_state:
					self.current_state.state = word
					print('solution found !')
					break
				else:
					self.current_state.parent = word
					children = self.generate_children(word)
					for child in children:
						child_curr_level.append(child)
			curr_search_level = child_curr_level.copy()
			child_curr_level.clear()
	#
	#
	#
	def find_path(self):
		curr_parent = self.goal_state
		r_path = Q.LifoQueue()
		queue_value = []
		while curr_parent != self.inital_state.state:
			
			for n in self.known_states:
				if n.state == curr_parent:
					r_path.put(n.state)
					curr_parent = n.parent
					break
		
		while r_path.qsize() > 0:
			self.update_path(r_path.get())
	#
	#
	#	
	def DFS(self):
		visited = []
		stack_path = deque()
		stack_path.append(self.current_state.state)
		visited.append(self.current_state.state)
		curr_children = self.generate_children(self.current_state.state)
		found = False

		while stack_path:
		#	print('visited: ', visited)
			if len(curr_children) != 0:
				new_state = curr_children.pop()
			if new_state == self.goal_state:
				found = True
				break
			elif new_state not in visited:
				visited.append(new_state)
				stack_path.append(new_state)
				curr_children = self.generate_children(new_state)
			elif len(curr_children)== 0 and new_state in visited:
				if stack_path[-1] == self.inital_state.state:
					break
				stack_path.pop()
				curr_children = self.generate_children(stack_path[-1])
		if found is False:
			print('no solution was found')
		if found is True:
			print('solution found: ', stack_path)
	# This method will take the start word from the arguments and generate the children 
	# then it will generate a list of tuples that are sorted in the priority queue based
	# on the huristic function
	#
	def informed_search(self):
		p_queue = Q.PriorityQueue()
		visited_nodes = []
		visited_nodes.append(self.current_state.state)
		curr_children = self.generate_children(self.current_state.state)
		found = True
		
		my_priority = self.heuristic(curr_children)
		for item in my_priority:
			p_queue.put(item)	

		while self.current_state.state != self.goal_state:
			if len(self.valid_dict) == len(visited_nodes):
				found = False
				break
			curr_tuple = p_queue.get(0)
			self.current_state.state = curr_tuple[0]
			visited_nodes.append(self.current_state.state)
			curr_children = self.generate_children(self.current_state.state)
		if found == False:
			return 'NO SOLUTION FOUND'
		else:
			return visited_nodes


	# This method takes a list of children and generates a priority based on the number of common 
	# letters the word shares with the goal state. Since the default behavior of a priority queue
	# is to sort the smallest priority to the front I calculate the inverse and take care of the 
	# special case where the inverse would be an invalid number 1/0 by adjusting its value to 2
	# so that it has a priority less than that of a word that shares 1 letter 
	def heuristic(self,cur_word_list):
		child_priority_process = []
		for word in cur_word_list:
			score = 0
			compare_words = zip(word, self.goal_state)
			for i in compare_words:
				if i[0] == i[1]:
					score += 1
			if score == 0:
				score += 2
			else:
				score = (1/score)
			child_priority_process.append((word,score))
		return child_priority_process
#class SolutionTreeGenerator(root):
	#def __init__(self):
	#def generate_children():
	#def validate_children():    

def main():

	program_option = input("""
Welcome to word latter generator. 
This program can take either a file with word pairs 
in the format: 'start_word' space 'end_word'
or manually enter word pairs 
		
Enter the number 1 if you want to use a list
Enter the number 2 if you want to enter words manually
Enter the number 0 if you want to exit
		""")
	
	if program_option == '0':
		print('Good Bye')
		return
	# selection for method loop
	while program_option != '0':
		#main selector loop 
		if program_option == '1':
			test_file = input('Enter the test file please: ')
		elif program_option == '2':
			start_word = input('Enter the starting word please: ')
			end_word = input('Enter the ending word please: ')
			while end_word == ' ' or start_word == ' ':
				print('You entered an invalid value for a word, try again:')
				start_word = input('Enter the starting word please: ')
				end_word = input('Enter the ending word please: ')

		# generate the agent for each method 
		if program_option == '1':
			
			with open(test_file) as f:
				test_list = []
				lines = f.readline().rstrip('\r\n')
				slines = lines.split(' ')
				test_list.append(tuple(slines[0],slines[1]))
			
			search_option = input(""" 
File loaded successfully.
				 
Enter the method you want to run on the file:
DFS = Depth First Search
BFS = Breadth First Search
IS  = Informed Search

values are not case sensitive
The files are going to be written to file solutions.txt
in the current working directory in order processed
				""")
			search_option.lower()
			
			while search_option != 'dfs' or search_option != 'bfs' or search_option != 'is':
				search_option = input ('Option selected not valid, please try again !')

			for i in test_list:
				MyAgent = Agent(i[0],i[1])
				MyAgent.create_dictionary()
				if search_option == 'dfs':
					MyAgent.DFS()
				elif search_option == 'bfs':
					MyAgent.BFS()
					MyAgent.find_path()
				elif search_option == 'is':
					MyAgent.informed_search()

		elif program_option == '2':
			search_option = input(""" 
Enter the method you want to run on the word pair: 
DFS = Depth First Search
BFS = Breadth First Search
IS  = Informed Search

values are not case sensitive
				""")
			search_option.lower()

			while search_option != 'dfs' and search_option != 'bfs' and search_option != 'is':
				search_option = input ('Option selected not valid, please try again !')

			MyAgent = Agent(start_word,end_word)
			MyAgent.create_dictionary()
			
			
			if search_option == 'dfs':
				MyAgent.DFS()
			elif search_option == 'bfs':
				MyAgent.BFS()
				MyAgent.find_path()
			elif search_option == 'is':
				MyAgent.informed_search()
			
		program_option = input(""" 
Want to continue ?
Enter the number of the option desired: 

Enter the number 1 if you want to use a list
Enter the number 2 if you want to enter words manually
Enter the number 0 if you want to exit
			   	       """)
main()
