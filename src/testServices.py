
#THIS FILE IS TO JUST TEST OUT THE SERVICES IN SERVER.PY. NOT PART OF THE FINAL PROJECT


from project.msg import State
from project.srv import *
import rospy


s = State(
    1,
    1,
    "EAST",
    0,
    ['dest1', 'dest2'],
    [False, False],
    [1.5,6],
    [1, 12],
    [0, 8],
    [3, 6]
)

def testGetSuccessors(state):    
    service = rospy.ServiceProxy('get_successors', GetSuccessor)
    while True:
        resp = service(state)
        succs = resp.succStates
        for i in succs:
            print str(i) + "\n\n"
        print str(resp.actions)+"\n"
        print str(resp.costs) + "\n"
        choice = int(input())
        state = succs[choice]

testGetSuccessors(s)

service = rospy.ServiceProxy('is_goal_state', IsGoalState)
response = service(s)
print response
s.destDeliveryStatus = [True, True]
response = service(s)
print response
