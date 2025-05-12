# 🚁 RAS598 Final Project: UAV Rock Detection and Localization in Simulated Terrain

This project implements a full PX4-based drone simulation pipeline using ROS 2 and Gazebo. The UAV performs:

- Simulated flight in a photogrammetry-based custom terrain with rocks  
- Real-time object detection using YOLOv8  
- Rock coordinate estimation using depth data and camera calibration  
- TF-based conversion of coordinates from camera to world frame  

---

## 📦 Prerequisites

Ensure you have the following installed:

- ROS 2 Humble or Jazzy  
- Gazebo Sim (`gz sim`)  
- PX4 Autopilot  
- Python 3.10+  
- `colcon`, `vcstool`, and `pip`  
- NVIDIA GPU (recommended for YOLO)

---

## 🧰 Installation & Setup

### 🔧 Step 1: Clone PX4 Autopilot

```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh
```

### 🔧 Step 2: Set up YOLO virtual environment

```bash
cd ~
python3 -m venv yolo
source ~/yolo/bin/activate
```

### 🔧 Step 3: Clone ROS 2 project and build

```bash
mkdir -p ~/ros2_project/src
cd ~/ros2_project/src
git clone https://github.com/btvvardhan/RAS598_project ros2_project
git clone https://github.com/PX4/px4_msgs.git

cd ~/ros2_project
colcon build  # Ensure you're in YOLO venv
```

### 🔧 Step 4: Install YOLOv8

```bash
pip install ultralytics
```

---

## 🚀 Running the System

### 1️⃣ Launch Drone and Controllers

```bash
ros2 launch ros2_project drone.launch.py
```

This:
- Launches PX4 drone in custom terrain world  
- Loads terrain and rocks via SDF  
- Starts:
  - TF broadcaster (`world ➝ camera`)
  - Velocity + keyboard control nodes  

### 2️⃣ Publish Camera Info

```bash
ros2 run ros2_project camera_info_publisher
```

This node:
- Subscribes to `/rgb_camera` and `/depth_camera`  
- Publishes:
  - `/synced/rgb_camera`
  - `/synced/depth_camera`
  - `/synced/rgb_camera/camera_info`

### 3️⃣ Run YOLO Detection

```bash
ros2 run ros2_project yolo
```

This node:
- Subscribes to `/synced/rgb_camera`  
- Detects rocks and creates bounding boxes  
- Publishes annotated image on `/annotated/rgb_camera/image`

### 4️⃣ Estimate Rock Coordinates

```bash
ros2 run ros2_project coordinates
```

This node:
- Uses:
  - Bounding box center (from YOLO)  
  - Depth (from `/synced/depth_camera`)  
  - Intrinsics (from `/synced/rgb_camera/camera_info`)  
- Estimates 3D coordinates of rocks in camera frame  
- Uses TF to convert to world frame  
- Publishes:
  - Bounding box overlay  
  - Rock marker at center  
  - `/final_image` for RViz2 visualization  

---

## 🧪 Tools Used

- **PX4**: Flight control and Gazebo integration  
- **Gazebo Sim**: Custom terrain simulation  
- **YOLOv8 (Ultralytics)**: Real-time object detection  
- **ROS 2**: Sensor data, TF, visualization, and control  
- **TF2**: Transforming rock coordinates to world frame  

---

## 📸 Visualization

Use RViz2 to view:
- `/final_image`
- TF tree
- Rock center markers

---

## 📁 Project Structure

```plaintext
ros2_project/
├── src/
│   ├── ros2_project/             # ROS 2 package with all Python nodes
│   └── px4_msgs/                 # PX4 message definitions
├── launch/
│   └── drone.launch.py           # Launches drone + control nodes
└── ros2_project/
    ├── yolo.py                   # Bounding box and labelling the stones
    ├── coordinates.py            # Saves rock coordinates and labels to CSV
    ├── camera_info_publisher.py  # Publishes synced camera topics
    ├── control.py                # Keyboard control interface
    ├── velocity_control.py       # Sends velocity commands to drone
    ├── processes.py              # Launch helper for PX4 and controls
    ├── odometry_tf_broadcaster.py # Broadcasts odometry TF
    └── best.pt                   # YOLOv8 model weights
```

---

## 👨‍💻 Authors

- **Teja Vishnu Vardhan Boddu**  
- **Vijayram Sriram Sathananthan**  
- **Harshvardhan**  

Team RAS 598 – *Space Robotics*
