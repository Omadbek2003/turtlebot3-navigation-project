# TurtleBot3 Navigation Project

Autonomous navigation simulation for TurtleBot3 in Gazebo, using ROS 1 Noetic, `move_base`, and `actionlib`. The robot navigates to predefined waypoints on a SLAM-generated map.

## Demo Videos

- [Autonomous navigation demo — part 1](https://youtu.be/jT3mdF-wUxQ)
- [Autonomous navigation demo — part 2](https://youtu.be/-_eWnJY-8sQ)

## Stack

- **OS:** Ubuntu 20.04
- **ROS:** Noetic
- **Simulator:** Gazebo 11
- **Navigation:** `move_base` (Nav Stack) + `actionlib`
- **Mapping:** SLAM (gmapping / cartographer)
- **Robot:** TurtleBot3 (Burger / Waffle)
- **Language:** Python

## Repository contents
turtlebot3_navigation_project/
├── package.xml          # ROS package manifest
├── CMakeLists.txt       # catkin build file
├── scripts/             # Python nodes (waypoint navigation)
├── maps/                # SLAM-generated occupancy grid
│   ├── promap.pgm
│   └── promap.yaml
└── src/                 # (empty — Python-only package)
## Dependencies

- `actionlib`
- `geometry_msgs`
- `move_base_msgs`
- `rospy`
- `turtlebot3_simulations` (third-party)
- `turtlebot3_navigation` (third-party)

## Build

Clone into your catkin workspace and build:

```bash
cd ~/catkin_ws/src
git clone https://github.com/YOUR_USERNAME/turtlebot3-navigation-project.git turtlebot3_navigation_project
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

## Run

```bash
# Terminal 1 — launch TurtleBot3 in Gazebo
export TURTLEBOT3_MODEL=burger
roslaunch turtlebot3_gazebo turtlebot3_world.launch

# Terminal 2 — launch navigation with the prebuilt map
roslaunch turtlebot3_navigation turtlebot3_navigation.launch \
    map_file:=$(rospack find turtlebot3_navigation_project)/maps/promap.yaml

# Terminal 3 — run the autonomous waypoint navigation node
rosrun turtlebot3_navigation_project cd_project.py
```

## Author

**Omadbek Teshaboyev**
QA Engineer @ DOMO · Founder @ Hairoom
[Telegram QA channel](https://t.me/omadbekqawork)

## License

MIT

