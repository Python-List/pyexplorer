#!/usr/bin/env python

import curses
import os
from string import center
from string import printable
from time import sleep
from sys import argv
from termcolor import colored

def check_arguments(arguments, ideal_arguments):

	invalid_arguments = [] #Will contain 'key' if value in that key:value pair is invalid.

	#Checking for normal arguments.
	for arg in arguments.keys():

		try: #Try-except here since there are some arguments which are not defined in ideal_arguments.
			if not arguments[arg] in allowed_args[arg]:

				invalid_arguments.append(arg)

		except KeyError: pass

	#Cheking for directory existence.
	try: #try-except since 'origin' may not exist in arguments dict.
		if not os.path.isdir(arguments['origin']):
			invalid_arguments.append('origin')

	except KeyError:
		pass

	if len(invalid_arguments)==0: #No invalid arguments, returns a tuple containing True at 0th positions
		return (False, None)

	else: #Invalid arguments exist, returns a tuple containing 'False' at 0th position.
		return (True, invalid_arguments)

def invalid_arg_reporter(arguments, invalid_arguments, do_exit=False): #On printing arguments, if exit is True, then exists the applications.

	os.system("clear")

	print "\n Please check your argument values:- \n"

	for index, arg in enumerate(arguments.keys()):

		if arg in invalid_arguments:
			print " "+str(index+1)+". "+arg+"="+colored(arguments[arg], color='white', on_color='on_red') #Print the key first and value with 'red' background. eg:- key=red_colored(value). It's red because this value will always be wrong.

		else:
			print " "+str(index+1)+". "+arg+"="+colored(arguments[arg], color='white', on_color='on_green') #Print the key first and value with 'green' background eg:- key=green_colored(value). It's red because this value will always be right.

	if do_exit:

		print #A horizontal space before leaving.
		exit()

def change_types(arguments):

	for key in arguments.keys():

		value = arguments[key]

		#Changing to boolean value if 'value' can be changed to boolean i.e. if 'value' is "True" or "False" written as strings.
		if value in ("True", "true", 1):
			arguments[key] = True

		elif value in ("False", "false", 0):
			arguments[key] = False

		#Changing to integer value if 'value' can be changed to integer i.e. if 'value' is a integer written as string.
		try: 
			arguments[key] = int(value)

		except:continue

	return arguments

def set_defaults(): #Sets default values to command line argument variables.

	global parent_navigation, show_hidden, origin

	parent_navigation = True

	show_hidden = False

	origin = '.'

set_defaults() #Setting up default values to command line argument variables.

str_booleans = ("True", "true", '1', "False", "false", '0') #A variable containing set of string versions of boolean "True" and "False".

#Setting up command-line arguments.

if len(argv[1:])>0: #If user has given arguments
			
	arguments = {} # An key:value version of command-line arguments i.e. argv[1:]

	for arg in argv[1:]: #Leaving the first element i.e. the filename.

		key, value = arg.split('=')
		arguments[key] = value

	allowed_args = {'show_hidden': str_booleans, 'parent_navigation': str_booleans} #These are the possible arguments and their respective possible values.

	invalid_arguments = check_arguments(arguments, allowed_args)

	if invalid_arguments[0]: #The first index i.e. 0th index will always be a boolean value i.e. True or False.

		invalid_arg_reporter(arguments, invalid_arguments[1], do_exit=True) # do exit if their is even one invalid argument value present.

	arguments = change_types(arguments) #Changing types if possible. Read comment inside that function.

	globals().update(arguments) #Variables declaration. eg:- parent_navigation, show_hidden etc.

#Initializes curses screen.
screen = curses.initscr()

screen.keypad(1) #Enable use of curses.KEY_UP, curses.KEY_DOWN etc. if it is enabled i.e. screen.keypad() is passed a value 1 instead of 0.

class manage(object):
	
	def __init__(self, parent_navigation, show_hidden, origin): #previous_directories a bool value which means wheather to include .. in the contents of current directories or not.

		self.update_dims() #getting screen dimensions.
		
		self.parent_navigation = parent_navigation

		self.show_hidden = show_hidden

		self.origin = origin #Defining 'self.origin' variable is useless here. But defined as per standard.

		os.chdir(self.origin) #Changing the initial path. We are not doing this with self.Chdir() method since we do not want to change self.dir_navigation(their is a possibility for changing this if done with self.Chdir() method.) and also don't want to set Signals since everything is intial.

		curses.start_color()

		#Color Pairs Specially For Files.
		curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_WHITE)
		curses.init_pair(2, curses.COLOR_WHITE , curses.COLOR_BLUE)

		#Color Pairs Specially For Directories
		curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
		curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA)

		#For credits
		curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)

		self.BOLD = [curses.A_NORMAL, curses.A_BOLD]

		screen.bkgd(" ", curses.color_pair(1)) #Foreground and Background color pair set to be 1st

		curses.noecho() #No echo of typed character.

		curses.curs_set(0) #0 For Cursor Invisible

		self.y = 1
		self.x = 0
		self.q = 0

		self.color_pair = 1
		self.selected = 0

		self.jumpchar = '.' #Initial jump character.

		self.dir_navigations = 0 #Stats the number of forward movements or backward movements in terms of numbers. It can be considered as 1 dimensional "vector" quantity. As we move forward(i.e. enters into the directories) then +1 is added, if backward then -1 is added to the variable's value at that time. 0 represents no movement(i.e. currently in the starting directory), -1(can be up-to -infinity) represents currently in the parent directory relative to the starting directory and similarly +1(can be up-to +infinity) represents currently in the child's directory relative to starting directory

		self.switch_extra_paths() #Creates a extra_paths variable that will be used to define dir_items i.e. immediately following line below.

		self.dir_items = self.extra_paths+os.listdir('.') #For initialization, it is needed, even Chdir method needs that dir_items should already exist.

		self.items_onscreen = self.dir_items #Items that will be shown on the screen.

		self.sorter() #Sorts dir_items. See comments in sorter method.

		self.slice_start = 0 #Starts slicing the dir_items from value 0 by default.

		self.SIG = 0 #define SIG:- Stands for "Signal" and means to recent key action. -1 represents KEY_UP, +1 represents KEY_DOWN, +2 represents ENTER, +3 represents HOME, +4 represents END and 0 represents initial State(i.e. no key pressed since the program was started).

		self.credits = "Developed By - Devesh"

		self.pre_printer()

	def refresh(self):

		if curses.is_term_resized(self.dims[0], self.dims[1]):
			self.pre_printer()

	def update_dims(self):

		self.dims = screen.getmaxyx()

	def sorter(self): #Breaks dir_items into two lists containing directories and files. Sort them individually in alphabetical order(lower case first) and them combines them.

		self.dir_items = sorted(self.dir_items, key=os.path.isdir, reverse=True) #Output order - Directories first then Files.

		dirs = []
		files = []

		for item in self.dir_items: #Seperates Directories and Files
			if os.path.isdir(item):
				dirs.append(item)
			else:
				files.append(item)

		dirs = sorted(dirs, key=str.lower) #Sorts seperated directories(alphabetical order, lower case first)

		files = sorted(files, key=str.lower) #Sorts seperated directories(alphabetical order, lower case first)

		if not self.show_hidden: #Don't show hidden files/directories.

			rm_hidden = [] #For dirs. Stands for 'removed hiddens'

			if len(dirs)>=2: #In case if the directory do not have any sub directories, correnposing this if-else condition is used.

				if dirs[1]=='..': #Due to parent_navigation, '..' is already removed. That's why wee need these conditions i.e. dirs[2:] and dirs[1:]
					mutable_dirs = dirs[2:] #mutable_dirs is same as 'dirs' but preserved reserved directory/directories i.e. '.' and '..'

				elif not dirs[1]=='..':
					mutable_dirs = dirs[1:]

			else:

				mutable_dirs = dirs[1:]

			for i in mutable_dirs: #Removing hidden directories.
					
				if not i[0]=='.':
					rm_hidden.append(i)

			dirs = self.extra_paths+rm_hidden

			rm_hidden = [] #For files. Stands for 'removed hiddens'

			for i in files: #Removing hidden files.
				if not i[0]=='.':
					rm_hidden.append(i)

			files = rm_hidden

		self.dir_items = dirs+files #Now finally dir_items have everything sorted.

	def switch_extra_paths(self):

		if not self.parent_navigation:

			if self.dir_navigations>0:
				self.extra_paths = ['.', '..']

			else:
				self.extra_paths = ['.']
		else:
			self.extra_paths = ['.', '..']
			
	def Chdir(self, switch_dir='.'): #A directory changing method which selects directory from selected region i.e. from self.selected, self.items_onscreen etc.

		if switch_dir=='.': #When variable is not set by user

			switch_dir = self.items_onscreen[self.selected]

		if os.path.isdir(switch_dir):
			
			if not (self.dir_navigations==0 and (not self.parent_navigation)) or switch_dir!='..': #Specially for goto_HOME method to block navigation to previous(..) directory on False parent_navigation

				os.chdir(switch_dir) #Changing the current working directory.

				if switch_dir=='..':
					self.dir_navigations-=1

				elif switch_dir=='.':
					pass

				else:
					self.dir_navigations+=1

				self.switch_extra_paths() #Updates the self.extra_paths variable.

				self.dir_items = self.extra_paths+os.listdir('.')
				
				self.sorter() #Sorting current directory items in alphabetical order.

				self.selected = 0

				self.SIG = 2 #Enter pressed Signal. SIG = 2

				self.pre_printer()

	def goto_Home(self):

		self.selected = 0

		self.SIG = 3

		self.pre_printer()

	def goto_END(self):

		self.SIG = 4

		self.pre_printer()
	
	def Move_Up(self):

		self.update_dims()

		if self.selected>0 or not self.items_onscreen[0]==self.dir_items[0]:

			self.SIG = -1 #KEY_UP signal stored.

			self.selected-=1

			self.pre_printer()

	def Move_Down(self):

		self.update_dims()

		if self.selected < len(self.items_onscreen)-1 or not self.items_onscreen[-1:]==self.dir_items[-1:]:

			self.SIG = 1 #KEY_DOWN signal stored.
			
			self.selected+=1

			self.pre_printer()

	def Jump(self, jumpchar): #Jump to filename/dirname starting with the given character.

		self.update_dims()

		self.first_chars = [ord(x[0].lower()) for x in self.dir_items] #A list containing first characters of elements of dir_items.

		if self.SIG == 5: #If last signal was a jumpchar signal then...

			if self.jumpchar == jumpchar: #...If the given character jumpchar is same as last one then...

				try: #...try to get next element's first character. (Try-except here for managing Index-error exception)

					if self.first_chars[self.jumpindex+1] == self.jumpchar:

						self.jumpindex += 1

						self.pre_printer()

						return True

					else: pass #We have passed it instead of returning something(breaking everything here) since selection is now at the end of possible element and we want to return to the first filename/dirname of pressed character on keyboard.

				except IndexError: pass #Same here as "else: pass" says.

			else: pass #Same here.

		else: pass #Same here

		try: #try-except here because there is possibility that no key available at that index.

			self.jumpindex = self.first_chars.index(jumpchar) #Index of the required element in dir_items.

		except ValueError:

			return False #Returning because we do not want signal to be stored since the signal wasn't executed.

		self.jumpchar = jumpchar

		self.SIG = 5 #5 key when any jumpchar key is pressed eg: a, b, g, z, 5, 9, 1...

		self.pre_printer()

	def goto_BACK(self):

		self.Chdir(switch_dir='..')

		self.SIG = 6 #Signal 6 -> Backspace key

		self.pre_printer()

	def pre_printer(self):

		self.update_dims()


		if self.SIG==-1: #UP Arrow Key
			
			if self.selected==-1: #Selected out of screen range in upper side. It simply means user requests for upper elements.
				
				self.selected+=1
				self.slice_start-=1


		elif self.SIG==1: #DOWN Arrow Key

			if self.selected==self.dims[0]-2: #Selected out of screen range in downward side. It simply means user requests for more elements from downwards.

				self.selected-=1
				self.slice_start+=1


		elif self.SIG==2: #ENTER Key
			
			self.slice_start = 0


		elif self.SIG==3: #HOME Key

			self.slice_start = 0


		elif self.SIG==4: #END Key

			if len(self.dir_items) > self.dims[0] - 2:

				self.selected = self.dims[0] - 3

				self.slice_start = len(self.dir_items)-(self.dims[0]-2)

			else:

				self.selected = len(self.dir_items)-1


		elif self.SIG==5: #Jumpchar keys.

			self.screen_start = self.dir_items.index(self.items_onscreen[0]) #Position of first item(on screen) in dir_items.

			self.screen_end = self.screen_start + (self.dims[0] - 3) #Position of last item(on screen) in dir_items.

			if self.screen_start <= self.jumpindex <= self.screen_end: #If the item we are looking for is on the screen then simply change self.selected value to select that.

				self.selected = self.jumpindex - self.screen_start

			else: #If the item we are looking for is not on the screen then...

				if self.jumpindex > self.screen_start + self.selected: #If index of required element is greater than the index we are on(selected item index.) then show selection at the end.

					self.slice_start = self.jumpindex - (self.dims[0] - 3)

					self.selected = self.dims[0] - 3

				else: #If index of required element is lesser than the index we are on(selected element index) then show selection at the top.

					self.slice_start = self.jumpindex

					self.selected = 0

		#Finally passing arguments to printer.
		self.printer(self.slice_start, (self.dims[0]-2)+self.slice_start)

		#Preserves self.slice_start value to be used in refreshing.

	def printer(self, slice_start=0, slice_end=1000): #1000 is assumption that none screen will have capacity to print more than 1000 characters.

		self.update_dims() #If terminal size have been resized.

		self.items_onscreen = self.dir_items[slice_start : slice_end] #self.dir_items is preserved to have an option for recovery.

		screen.clear()

		for y, dir_item in enumerate(self.items_onscreen): #Setting configurations to color up directories when printed.

			if os.path.isdir(dir_item):
				
				dir_item = "+ "+dir_item
				
				if y==self.selected: #When the current directory is selected.
					self.bold = 1
					self.color_pair = 4

				else:
					self.bold = 1
					self.color_pair = 3

			elif not os.path.isdir(dir_item): #Setting configurations to color up directories when printed.
				
				dir_item = "  "+dir_item #Indentation because of symmetry with "+" before directory(ies) names.
				
				if y==self.selected: #When the current file is selected.
					self.color_pair = 2
					self.bold = 1

				else:
					self.color_pair = 1
					self.bold = 0

			#Current working directory. Top of window.
			screen.addstr(0, 0, center(os.getcwd(), self.dims[1]-10), curses.color_pair(3) | self.BOLD[1])

			#Credits to Developer.
			screen.addstr(self.dims[0]-1, self.dims[1]-len(" "+self.credits+" ")-1, " "+self.credits+" ", curses.color_pair(5) | self.BOLD[1])

			#Printing elements and backgrounds.
			screen.addstr(y+1, self.x, " "+dir_item+(self.dims[1]-len(dir_item)-1)*" ", curses.color_pair(self.color_pair) | self.BOLD[self.bold])

	def end(self):
		curses.endwin()

browser = manage(parent_navigation, show_hidden, origin)
q = 0

while q!=81: #ASCII code 81 = 'Q'

	q = screen.getch()

	if q==10:

		browser.Chdir()

	elif q==curses.KEY_DOWN:

		browser.Move_Down()

	elif q==curses.KEY_UP:

		browser.Move_Up()

	elif q==curses.KEY_HOME:

		browser.goto_Home()

	elif q==curses.KEY_END:

		browser.goto_END()

	elif q in [ord(x) for x in printable]:

		browser.Jump(q)

	elif q==curses.KEY_BACKSPACE:

		browser.goto_BACK()

	screen.timeout(100)

	browser.refresh()

browser.end()
