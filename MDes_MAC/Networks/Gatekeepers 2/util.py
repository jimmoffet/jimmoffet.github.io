import random
from math import sqrt,cos,sin,atan2

########################################
#   Mandatory functions for the rrt    #
########################################

# Tests if the new_node is close enough to the goal to consider it a goal
def winCondition(new_node,goal_node,WIN_RADIUS):
    """
    new_node - newly generated node we are checking
    goal_node - goal node
    WIN_RADIUS - constant representing how close we have to be to the goal to
        consider the new_node a 'win'
    """

    x1,y1 = new_node
    x2,y2 = goal_node
    distance = sqrt (float(x2 - x1)**2 + float(y2 - y1)**2)
    if distance <= WIN_RADIUS:
        return True
    else:
        return False


# Find the nearest node in our list of nodes that is closest to the new_node
def nearestNode(nodes,new_node):
    """
    nodes - a list of nodes in the RRT
    new_node - a node generated from getNewPoint
    """

    x1,y1 = new_node
    oldDistance = float('inf')
    nearestNode = ()
    for node in nodes:
        x2,y2 = node
        distance = sqrt (float(x2 - x1)**2 + float(y2 - y1)**2)
        if distance < oldDistance:
            nearestNode = node
            oldDistance = distance
    return nearestNode


# Find a new point in space to move towards uniformally randomly but with
# probability 0.05, sample the goal. This promotes movement to the goal.
def getNewPoint(XDIM,YDIM,XY_GOAL):
    """
    XDIM - constant representing the width of the game
    YDIM - constant representing the height of the game
    XY_GOAL - node (tuple of integers) representing the location of the goal
    """
    
    
    if random.random() < 0.05:
        return XY_GOAL
    else:
        randomX = random.randint(0, XDIM-1)
        randomY = random.randint(0, YDIM-1)
        return (randomX,randomY)


# Extend (by at most distance delta) in the direction of the new_point and place
# a new node there
def extend(current_node,new_point,delta):
    """
    current_node - node from which we extend
    new_point - point in space which we are extending toward
    delta - maximum distance we extend by
    """

    x1,y1 = current_node
    x2,y2 = new_point
    dx = x2 - x1
    dy = y2 - y1
    new_node = ()
    distance = sqrt(dx**2 + dy**2)
    
    if distance <= delta:
        new_node = new_point
    else:
        radians = atan2(dy,dx)
        new_dy = sin(radians)*delta
        new_dx = cos(radians)*delta
        new_x = x1 + new_dx
        new_y = y1 + new_dy
        new_node = (new_x , new_y)

    return new_node


# iterate throught the obstacles and check that our point is not in any of them
def isCollisionFree(obstacles,point,obs_line_width):
    """
    obstacles - a dictionary with multiple entries, where each entry is a list of
        points which define line segments of with obs_line_width
    point - the location in space that we are checking is not in the obstacles
    obs_line_width - the length of the line segments that define each obstacle's
        boundary
    """
    
    # for each obstacle, get the separate lines (coordinateTuple, coordinateTuple)
    lines = []
    for j in range(len(obstacles)):
        obstacle = obstacles[j]
        for i in range(len(obstacle)-1):
            line = (obstacle[i],obstacle[i+1])
            lines.append(line)
    
    x_0, y_0 = point
    
    # for each line get the closest point on the line
    for line in lines:
        x_1 , y_1 = line[0]
        x_2 , y_2 = line[1]
        min_x = min(x_1,x_2)
        max_x = max(x_1,x_2)
        min_y = min(y_1,y_2)
        max_y = max(y_1,y_2)
        #line formula: y = mx + k
        if x_2 - x_1 == 0:
            # check if closest point is on the line
            if min_y <= y_0 <= max_y:
                # check if point is too close
                if abs(x_0 - x_2) <= obs_line_width:
                    return False          
        elif y_2 - y_1 == 0:
            # check if closest point is on the line
            if min_x <= x_0 <= max_x:
                # check if point is too close
                if abs(y_0 - y_2) <= obs_line_width:
                    return False                 
        else:
            m = (float(x_2) - x_1)/(y_2 - y_1)
            k = y_2 - (m * x_2)
            #closest point on original line
            x_c = (x_0 + ( m * y_0 ) - (m * k)) / ((m**2) + 1)
            #y_c = m * x_c + k
            # check if closest point is on the line
            if (min_x - obs_line_width/2) <= x_c <= (max_x + obs_line_width/2): # and min_y - obs_line_width/2 <= y_c <= max_y + obs_line_width/2:
                # check if point is too close
                distance_0c = abs(k + (m * x_0) - y_0) / sqrt(1 + (m**2))                
                if distance_0c <= obs_line_width:
                    return False
    return True
        


################################################
#  Any other helper functions you need go here #
################################################
