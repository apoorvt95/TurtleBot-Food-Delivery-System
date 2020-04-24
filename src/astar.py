#!/usr/bin/env python

from project.msg import State
from project.srv import *
from std_msgs.msg import String
import rospy
import time
import itertools
import heapq


rospy.init_node("astar")
goal_state_x = []
goal_state_y = []

publisher = rospy.Publisher("/actions", String, queue_size=10)

def manhattanDistance(x1, y1, destDeliveryStatus):
    """
    This function returns manhattan distance between two points.
    """
    m = 0
    for i in range(len(goal_state_x)):
        if(destDeliveryStatus[i]==False):
            m = max(m, (abs(x1-goal_state_x[i]) + abs(y1-goal_state_y[i])))
    
    return m

def astar():
    '''
    Perform A* search to find sequence of actions from initial state to goal state
    '''
    get_successor = rospy.ServiceProxy('get_successors', GetSuccessor)
    is_goal_state = rospy.ServiceProxy('is_goal_state', IsGoalState)
    get_initial_state = rospy.ServiceProxy('get_initial_state', GetInitialState)
    init_state = get_initial_state().s
    for i in range(len(init_state.destXCoord)):
        goal_state_x.append(init_state.destXCoord[i])
        goal_state_y.append(init_state.destYCoord[i])
    destSTime = init_state.destTimeStart
    destETime = init_state.destTimeEnd

    for i in range(len(init_state.destXCoord)):
        print "Goal state ", i, " coordinates x: ", goal_state_x[i], " y: ", goal_state_y[i], "Time Constraints Start Time: ", destSTime[i], "End Time: ", destETime[i]
    counter = itertools.count()
    q = []
    frontier = [str(init_state)]
    heapq.heappush(q, [manhattanDistance(init_state.robotX, init_state.robotY, init_state.destDeliveryStatus), next(counter), init_state, 0, []])
    visited_states = set()
    action_list = []
    while(q):
        [path_cost, count, curr_state, cost_till_here, action_path] = heapq.heappop(q)
        frontier.remove(str(curr_state))
        #print is_goal_state(curr_state).res
        #print action_path
        #print cost_till_here
        if is_goal_state(curr_state).res:
            action_list = action_path
            break
        visited_states.add(str(curr_state))
        successor = get_successor(curr_state)
        [possible_next_state, state_costs, actions_toreach_state] = [successor.succStates,successor.costs,successor.actions]
        for i in range(len(possible_next_state)):
            
            next_state = possible_next_state[i]
            destTime = next_state.destTimeEnd
            destStatus = next_state.destDeliveryStatus
            curr_time = next_state.time
            minTime = sys.maxint
            ind = 0
            for j in range(len(destTime)):
                if(destTime[j]<minTime and destStatus[j]==False):
                    minTime=destTime[j]
                    ind = j
            if(curr_time>minTime):
                continue
            cost = state_costs[i]
            action = actions_toreach_state[i]
            if ((str(next_state) not in visited_states) and (str(next_state) not in frontier)):
                frontier.append(str(next_state))
                heapq.heappush(q,[cost_till_here + cost + manhattanDistance(next_state.robotX, next_state.robotY, next_state.destDeliveryStatus), next(counter), next_state, cost_till_here + cost, action_path + [action]])
            elif(str(next_state) in frontier):
                for sublist in list(q):
                    if(str(sublist[2])==str(next_state) and sublist[3]>cost_till_here+cost):
                        q.remove(sublist)
                        heapq.heappush(q,[cost_till_here + cost + manhattanDistance(next_state.robotX, next_state.robotY, next_state.destDeliveryStatus), next(counter), next_state, cost_till_here + cost, action_path + [action]])
                        break
    return action_list


def exec_action_list(action_list):
    '''
    publishes the list of actions to the publisher topic
    action_list: list of actions to execute
    '''
    plan_str = '_'.join(action for action in action_list)
    publisher.publish(String(data = plan_str))


if __name__ == "__main__":
    # DO NOT MODIFY BELOW CODE
    start_time = time.time()
    actions = astar()
    if(len(actions)==0):
        print "Not able to find plan which satisfies the time constraints"
    time_taken = time.time() - start_time
    print("Time Taken = " + str(time_taken))
    if(len(actions)!=0):
        print("Plan = " + str(actions) + "Time = " + len(actions))
    exec_action_list(actions)

  #  exec_action_list(actions)

