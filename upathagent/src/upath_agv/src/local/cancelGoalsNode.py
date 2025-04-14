#!/usr/bin/env python3

import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal


import actionlib_tutorials.msg


if __name__ == '__main__':
    try:
        rospy.init_node('cancel_goal')
        client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        wait = client.wait_for_server(rospy.Duration(1))
        client.cancel_all_goals()
        # client.cancel_goals_at_and_before_time()
    except rospy.ROSInterruptException:
        pass