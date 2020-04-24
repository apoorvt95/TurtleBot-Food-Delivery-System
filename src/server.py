#!/usr/bin/env python

from project.msg import State
from project.srv import *
from mazeGen import *
import rospy
import sys
import argparse
import time
import json
import random
import os

parser = argparse.ArgumentParser()
parser.add_argument('-houses', help='for providing number of houses', metavar='5', action='store', dest='houses', default=2, type=int)
parser.add_argument('-s', help='for providing random seed', metavar='32', action='store', dest='seed', default=2, type=int)
parser.add_argument('-f', help='for toggling time constraints', metavar='32', action='store', dest='f', default=0, type=int)

f=0

def handle_get_initial_state(req):
    """
    This function will return initial state of turtlebot3.
    """

    initial_state = State()
    initial_state.robotX = 0
    initial_state.robotY = 0
    initial_state.time = 0
    initial_state.direction = "EAST"
    initial_state.destXCoord = []
    initial_state.destYCoord = []
    initial_state.destTimeStart = []
    initial_state.destTimeEnd = []
    initial_state.destDeliveryStatus = []
    initial_state.destNames = []   
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    file_path = root_path + "/houses.json"
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)  
        for k in data['houses']:
            initial_state.destNames.append(k)
            initial_state.destXCoord.append(data['houses'][k]['load_loc'][0][0]) 
            initial_state.destYCoord.append(data['houses'][k]['load_loc'][0][1])
            initial_state.destDeliveryStatus.append(False)
            if(f==0):
                startTime = random.randint(0,houses*2)
                finishTime = startTime  + random.randint(0, 15)
            else:
                startTime = 0
                finishTime = 100
            initial_state.destTimeStart.append(startTime)
            initial_state.destTimeEnd.append(finishTime)
    return GetInitialStateResponse(initial_state)

def handle_is_goal_state(req):
    req = req.s
    print str(req)
    for i in range(len(req.destNames)):
        if not req.destDeliveryStatus[i]:
            return IsGoalStateResponse(False)
    return IsGoalStateResponse(True)

def handle_get_successor(req):
    action_list = ["TurnCW", "TurnCCW", "MoveB", "MoveF"]
    direction_list = ["NORTH", "EAST", "SOUTH", "WEST"]
    state_cost = []
    succ_states = []
    req = req.currState

    for action in action_list:
        #Checking requested action and making changes in states
        x_cord, y_cord, direction, t = req.robotX, req.robotY, req.direction, req.time
        if action == 'TurnCW':
            index = direction_list.index(req.direction)
            direction = direction_list[(index+1)%4]        
            g_cost = 0    

        elif action == 'TurnCCW':
            index = direction_list.index(req.direction)
            direction = direction_list[(index-1)%4]
            g_cost = 0

        elif action == 'MoveF':
            if direction == "NORTH":
                y_cord += 0.5
            elif direction == "EAST":
                x_cord += 0.5
            elif direction == "SOUTH":
                y_cord -= 0.5
            elif direction == "WEST":
                x_cord -= 0.5
            g_cost = 0.5

        elif action == 'MoveB':
            if direction == "NORTH":
                y_cord -= 0.5
            elif direction == "EAST":
                x_cord -= 0.5
            elif direction == "SOUTH":
                y_cord += 0.5
            elif direction == "WEST":
                x_cord += 0.5
            g_cost = 0.5

        if req.robotX <= x_cord and req.robotY <= y_cord:
            isValidEdge = check_is_edge((req.robotX, req.robotY, x_cord, y_cord), "changedValuesLater")
        else:
            isValidEdge = check_is_edge((x_cord, y_cord, req.robotX, req.robotY), "changedValuesBefore")

        statuses = list(req.destDeliveryStatus)
        updateDeliveryStatus(req.destXCoord, req.destYCoord, req.destTimeStart, req.destTimeEnd, t+1, statuses, x_cord, y_cord)

        if not isValidEdge:
            s = State(-1, -1, direction, t+1, req.destNames, statuses, req.destXCoord, req.destYCoord, req.destTimeStart, req.destTimeEnd)
            state_cost.append(-1)
        else:
            s = State(x_cord, y_cord, direction, t+1, req.destNames, statuses, req.destXCoord, req.destYCoord, req.destTimeStart, req.destTimeEnd)
            state_cost.append(g_cost)

        succ_states.append(s)

    return GetSuccessorResponse(succ_states, state_cost, action_list)

def updateDeliveryStatus(xCoords, yCoords, startTimes, endTimes, t, statuses, x, y):
    for i in range(len(statuses)):
        if x==xCoords[i] and y==yCoords[i] and t >= startTimes[i] and t<=endTimes[i]:
            statuses[i]=True

def check_is_edge(coords, flagStr):
    #TO DO: this needs to be implemented
    return True

if __name__ == "__main__":
    args = parser.parse_args()
    if(args.houses):
        houses = args.houses
    if(args.seed):
        seed = args.seed
    if(args.f):
        f = args.f    
    grid_size = houses*6
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

    mObj = Maze(grid_size)
    mazeInfo = mObj.generate_blocked_edges(seed,  houses, root_path)#,0.5)

    rospy.init_node('get_successor_server')
    rospy.Service('is_goal_state', IsGoalState, handle_is_goal_state)
    rospy.Service('get_successors', GetSuccessor, handle_get_successor)
    rospy.Service('get_initial_state', GetInitialState, handle_get_initial_state)
    print "Server is running, Houses ", houses

    rospy.spin()


