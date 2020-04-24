from collections import defaultdict
import numpy as np
import argparse
import random
import pprint
import json
import copy

class Maze:

	def __init__(self, grid_dimension, myscale=0.5):
		self.food_list = ["Chinese","Italian","Indian","Middle Eastern","Japanese","Korean","Mongolian","American","Mexican",
                    "Thai","Vietnamese","BBQ","Soul Food","Greek","Lebanese"]

		self.grid_dimension = grid_dimension
		self.grid_start = 0
		self.myscale = myscale
		self.blocked_edges = set()

	def __deepcopy__(self, memodict={}):
		new_maze = Maze(self.grid_dimension)
		new_maze.blocked_edges = copy.deepcopy(self.blocked_edges)
		return new_maze

	def copy_empty_world(self,root_path):
		f_in = open(root_path+'/worlds/empty_world.sdf', 'r')
		f_out = open(root_path+'/worlds/maze.sdf', 'w')
		for line in f_in:
			f_out.write(line)
		f_in.close()
		return f_out

	def add_walls_description(self,f_out):
		for i in range(1, 5):
			f_out.write('<model name=\'wall{}\'>\n'.format(i))
			f_out.write('<static>1</static>\n<link name=\'link\'>\n<pose frame=\'\'>0 0 0.42 0 -0 0</pose>\n<collision name=\'collision\'>\n<geometry>\n<box>\n<size>7.5 0.2 2.8</size>\n</box>\n')
			f_out.write('</geometry>\n<max_contacts>10</max_contacts>\n<surface>\n<contact>\n<ode/>\n</contact>\n<bounce/>\n<friction>\n<torsional>\n<ode/>\n</torsional>\n<ode/>\n</friction>\n</surface>\n</collision>\n')
			f_out.write('<visual name=\'visual\'>\n<cast_shadows>0</cast_shadows>\n<geometry>\n<box>\n<size>7.5 0.2 2.8</size>\n</box>\n</geometry>\n<material>\n<script>\n')
			f_out.write('<uri>model://grey_wall/materials/scripts</uri>\n<uri>model://grey_wall/materials/textures</uri>\n<name>vrc/grey_wall</name>\n</script>\n</material>\n</visual>\n<self_collide>0</self_collide>\n')
			f_out.write('<kinematic>0</kinematic>\n<gravity>1</gravity>\n</link>\n<pose frame=\'\'>-0.779308 4.01849 0 0 -0 0</pose>\n</model>\n')

	def add_walls(self,f_out, length):
		scale = (length+2)/7.5
		wall_dimensions = [(-1, length/2, -1.55905, scale, 1), (length/2, length+1, 0, scale, 1), (length+1, length/2, -1.55905, scale, 1), (length/2, -1, 0, scale, 1)]
		for i in range(4):
			f_out.write('<model name=\'wall{}\'>\n'.format(i+1))
			f_out.write('<pose frame=\'\'>{} {} 0 0 -0 {}</pose>\n'.format(wall_dimensions[i][0], wall_dimensions[i][1], wall_dimensions[i][2]))
			f_out.write('<scale>{} {} 0.03</scale>\n'.format(wall_dimensions[i][3], wall_dimensions[i][4]))
			f_out.write('<link name=\'link\'>\n')
			f_out.write('<pose frame=\'\'>{} {} 0.42 -0 0 {}</pose>\n'.format(wall_dimensions[i][0], wall_dimensions[i][1], wall_dimensions[i][2]))
			f_out.write('<velocity>0 0 0 0 -0 0</velocity>\n<acceleration>0 0 0 0 -0 0</acceleration>\n<wrench>0 0 0 0 -0 0</wrench>\n</link>\n</model>\n')


	def add_house_description(self,f_out, coords):
		food_count = -1
		for z, i in enumerate(coords):
			x, y = i
			if z % 2 == 0:
				scale = 0.5
				food_count += 1
			else:
				scale = 0.3
			f_out.write("<model name='House 1 {0}\'>/n".format(z+1))
			f_out.write("<static>true</static>/n<link name='link'>/n<collision name='collision'>/n<geometry>/n<mesh>/n<uri>model://house_1/meshes/house_1.dae</uri>/n<scale>0.01 0.01 0.01</scale>/n</mesh>/n</geometry>/n</collision>/n<visual name='visual'>/n<geometry>/n<mesh>/n<uri>model://house_1/meshes/house_1.dae</uri>/n<scale>1.5 1.5 1.5</scale>/n</mesh>/n</geometry>/n<material>/n<script>/n<uri>model://house_1/materials/scripts</uri>/n<uri>model://house_1/materials/textures</uri>/n<name>House_1/Diffuse</name>/n</script>/n<shader type='normal_map_tangent_space'>/n<normal_map>House_1_Normal.png</normal_map>/n</shader>/n</material>/n</visual>/n</link>/n</model>")

	def add_house(self, f_out, x, y, scale, houses_count):
		f_out.write("<model name='House 1 {0}'>".format(houses_count))
		f_out.write("<pose frame=''>{0} {1} 0 0 -0 0</pose>".format(x, y))
		f_out.write("<scale>{0} {0} 0.05</scale>".format(scale))
		f_out.write("<link name='link_20'>")
		f_out.write("<pose frame=''>{0} {1} 0 0 -0 0</pose>".format(x, y))
		f_out.write("<velocity>0 0 0 0 -0 0</velocity>")
		f_out.write("<acceleration>0 0 0 0 -0 0</acceleration>")
		f_out.write("<wrench>0 0 0 0 -0 0</wrench>")
		f_out.write("</link>")
		f_out.write("</model>")

	def house_dict_generator(self,house, house_counter, size, access_loc_list, location, food_count_index):
		house["house_"+str(house_counter)]["size"] = size
		house["house_"+str(house_counter)]["type"] = self.food_list[food_count_index]
		house["house_"+str(house_counter)]["loc"]= location
		house["house_"+str(house_counter)]["load_loc"] = access_loc_list

	def add_bloced_edges(self,x, y):
		blocked_list = []

		x_dec = 0.5
		y_dec = 0.5
		blocked_list.append((x-x_dec, y))
		blocked_list.append((x+x_dec, y))
		blocked_list.append((x, y-y_dec))
		blocked_list.append((x, y+y_dec))
		return blocked_list

	def generate_blocked_edges(self, seed, number_of_houses, root_path):
		object_dict = {}
		houses = {}
		np.random.seed(seed)
		list_of_list_of_coords = []
		f_out = self.copy_empty_world(root_path)
		self.add_walls(f_out, self.grid_dimension*self.myscale)

		nhouses = number_of_houses
		housesCoords = []
		houses_count = 1
		# x = random.randint(0,self.grid_dimension//4+ 2)
		# y = random.randint(0,self.grid_dimension//4+ 2)
		food_count = -1
		houses = {}
		while(houses_count <= nhouses):
			x = random.randint(1,self.grid_dimension/4+3)
			y = random.randint(1,self.grid_dimension/4+3)
			scale = 0.05
			size = "large"
			houses["house_"+str(houses_count)] = {}
			housesCoords.append((x,y))
			for i in range(2):
				for j in range(2):
					self.blocked_edges.add((x+i*0.5,y + j*0.5,x+i*0.5 + 0.5,y+j*0.5))
					self.blocked_edges.add((x+i*0.5,y + j*0.5,x+i*0.5,y+j*0.5+0.5))
					self.blocked_edges.add((x+i*0.5,y + j*0.5,x+i*0.5,y+j*0.5-0.5))
					self.blocked_edges.add((x+i*0.5 - 0.5,y + j*0.5,x+i*0.5,y+j*0.5))
			blocked_list = [(x-0.5,y),(x,y-0.5),(x-0.5,y+0.5),(x,y+1),(x+1,y+0.5),(x+0.5,y+1),(x+1,y),(x+0.5,y-0.5)]
            # food_count = random.randint(0,len(self.food_list))
			self.house_dict_generator(houses, houses_count, size, blocked_list, (x, y), random.randint(0,9))
			self.add_house(f_out, x, y,scale, houses_count)
			houses_count += 1
			# if (houses_count-1) % 3 == 0:
			# 	x += 2
			# 	y = 1
			# else:
			# 	y += 2

		f_out.write('</state>')

		self.add_house_description(f_out, housesCoords)
		self.add_walls_description(f_out)

		f_out.write('</world>\n</sdf>')
		f_out.close()

		object_dict["houses"] = houses
	 	with open(root_path + '/houses.json', 'w') as fp:
	 		json.dump(object_dict, fp)

	 	return object_dict
