#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import PointStamped
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from collections import deque
import threading
import time

class SimpleNavigator:
    def __init__(self):
        rospy.init_node("basic_navigator", anonymous=False)
        
        # Action client for move_base
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        rospy.loginfo("⏳ Connecting to navigation system...")
        if not self.client.wait_for_server(timeout=rospy.Duration(60)):
            rospy.logerr("🛑 Navigation system offline!")
            rospy.signal_shutdown("Action server not available")
            return
        
        self.queue = deque()
        self.active = False
        self.auto = False
        self.goal_sub = rospy.Subscriber("/clicked_point", PointStamped, self.add_goal)
        
        # Start terminal interface
        self.interface_thread = threading.Thread(target=self.terminal_interface)
        self.interface_thread.daemon = True
        self.interface_thread.start()
        
        rospy.loginfo("🟢 Ready! Click goals in RViz")
        rospy.loginfo("Commands: go | auto | manual | clear | about | break")

    def terminal_interface(self):
        while not rospy.is_shutdown():
            try:
                cmd = input().strip().lower()
                if cmd == "go":
                    self.start_nav()
                elif cmd == "auto":
                    self.auto = True
                    rospy.loginfo("🔄 AUTO: Will auto-start after goals")
                elif cmd == "manual":
                    self.auto = False
                    rospy.loginfo("🔄 MANUAL: Type 'go' to start")
                elif cmd == "clear":
                    self.queue.clear()
                    rospy.loginfo("🗑️ Goals cleared!")
                elif cmd == "about":
                    rospy.loginfo(f"📊 Status: {'Active' if self.active else 'Idle'} | Queue: {len(self.queue)}")
                elif cmd == "break":
                    self.stop_nav()
                    rospy.loginfo("🛑 Navigation interrupted")
                else:
                    rospy.logwarn("❓ Unknown cmd. Try: go, auto, manual, clear, about, break")
            except Exception as e:
                time.sleep(0.1)

    def add_goal(self, msg):
        try:
            x, y = msg.point.x, msg.point.y
            self.queue.append((x, y, 1.0))
            rospy.loginfo(f"🎯 Added: ({x:.1f}, {y:.1f}) | Total: {len(self.queue)}")
            
            if self.auto and not self.active:
                self.start_nav()
        except Exception as e:
            rospy.logerr(f"⚠️ Goal error: {str(e)}")

    def start_nav(self):
        if not self.queue:
            rospy.logwarn("🚫 No goals queued!")
            return
        if self.active:
            rospy.logwarn("🛑 Already navigating!")
            return
            
        rospy.loginfo("🧭 Starting mission!")
        self.active = True
        self.process_queue()

    def stop_nav(self):
        self.active = False
        self.client.cancel_all_goals()
        self.queue.clear()

    def process_queue(self):
        if not self.active or not self.queue:
            rospy.loginfo("🏁 Mission complete! Waiting for new goals...")
            self.active = False
            return

        # Cancel current goal if active
        if hasattr(self, '_has_active_goal'):
            self.client.cancel_goal()
            time.sleep(0.3)

        x, y, w = self.queue[0]
        goal = self.create_goal(x, y, w)
        
        rospy.loginfo(f"🚀 Going to: ({x:.1f}, {y:.1f})")
        self.client.send_goal(goal, 
                           done_cb=self.done_callback,
                           feedback_cb=self.feedback_callback)
        self._has_active_goal = True
        self.queue.popleft()

    def create_goal(self, x, y, w):
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        goal.target_pose.pose.orientation.w = w
        return goal

    def feedback_callback(self, feedback):
        pos = feedback.base_position.pose.position
        rospy.loginfo_once(f"📍 Moving... Current: ({pos.x:.1f}, {pos.y:.1f})")

    def done_callback(self, status, result):
        del self._has_active_goal
        if status == actionlib.GoalStatus.SUCCEEDED:
            rospy.loginfo("✅ Goal reached!")
        else:
            rospy.logwarn(f"❌ Failed! Code: {status}")
        
        rospy.Timer(rospy.Duration(0.5), lambda _: self.process_queue(), oneshot=True)

if __name__ == "__main__":
    try:
        navigator = SimpleNavigator()
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("🛑 Node stopped")
