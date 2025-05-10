
# 🛰️ Autonomous Drone Task: Search, Localize, and Land — PX4 + ROS 2

This repository hosts a ROS 2 package enabling a fully autonomous drone routine in Gazebo using PX4 SITL. The mission comprises:

- Controlled Vertical Takeoff and Hover
- ArUco Marker Recognition for Visual Targeting
- Vision-Based Precision Landing
- Real-Time Energy Monitoring and Range Estimation

---

## 🔧 System Architecture and Nodes

Four ROS 2 nodes power the autonomous flight sequence:

| Node Name | Functionality |
|-----------|---------------|
| `takeoff_and_hover.py` | Arms drone, initiates OFFBOARD mode, takes off to a defined altitude, and maintains a hover |
| `aruco_landing.py` | Identifies ArUco markers via camera feed and guides the drone to land when aligned |
| `dimension_estimator.py` | Uses marker pixel size to estimate distance from camera using pinhole projection |
| `energy_logger.py` | Tracks the drone’s flight path, calculates total travel distance, and estimates energy usage |

> **Note**: The onboard camera of the `x500_depth` model has been modified to point downward for marker detection.

---

### 🧠 Node: `dimension_estimator.py`

This node estimates the physical distance between the drone and the detected ArUco marker in the environment using camera geometry.

**Data Sources:**

- Topic: `/rgb_camera`
- ArUco detection via OpenCV
- Pinhole camera model for distance inference

**Process Overview:**

| Step | Detail |
|------|--------|
| 1 | Subscribes to RGB image feed |
| 2 | Detects ArUco markers in real-time |
| 3 | Extracts marker width in pixel space |
| 4 | Applies camera intrinsics to estimate range |
| 5 | Outputs estimated distance in meters |

---

### 📊 Core Parameters

| Parameter | Value | Notes |
|----------|-------|-------|
| Marker Size | `0.2 m` | Real-world physical marker width |
| Focal Length | `554.0 px` | Approximate camera intrinsics |

---

### 📐 Range Estimation Formula

\[
\text{Distance} = \frac{f_x \cdot \text{Marker Real Size}}{\text{Marker Pixel Width}}
\]

---

### ⚡ Node: `energy_logger.py`

This node is responsible for calculating flight distance and estimating energy expenditure based on odometry.

**Key Functionalities:**

| Step | Description |
|------|-------------|
| 1 | Subscribes to PX4 odometry (`/fmu/out/vehicle_odometry`) |
| 2 | Monitors drone’s `(x, y, z)` positions |
| 3 | Calculates stepwise distances |
| 4 | Aggregates total distance |
| 5 | Estimates energy based on 1 unit/meter assumption |

---

## ✈️ Flight Control Nodes

### `takeoff_and_hover.py`
- Automatically arms the drone
- Switches into **OFFBOARD** mode
- Takes off vertically to **15 meters**
- Maintains a stable hover
- Publishes to `/fmu/in/trajectory_setpoint`

---

### `aruco_landing.py`
- Receives frames from `/rgb_camera`
- Detects ArUco marker using OpenCV
- Calculates offset between marker center and image center
- Applies velocity correction using `/cmd_vel`
- Lands drone when marker is centered in view

---

## 🧪 How to Run the System

1. **Launch Gazebo with Drone and Marker:**

```bash
ros2 launch terrain_mapping_drone_control cylinder_landing.launch.py
```

2. **Start Micro XRCE Agent:**

```bash
MicroXRCEAgent udp4 -p 8888
```

3. **Takeoff Node:**

```bash
ros2 run terrain_mapping_drone_control takeoff_and_hover.py
```

4. **Run ArUco Landing Node:**

```bash
ros2 run terrain_mapping_drone_control aruco_landing.py
```

5. **Run Dimension Estimator:**

```bash
ros2 run terrain_mapping_drone_control dimension_estimator.py
```

6. **Run Energy Logger:**

```bash
ros2 run terrain_mapping_drone_control energy_logger.py
```

---

## 🔁 ROS Graph

```bash
rqt_graph
```

---

## ✅ Final Output

The drone:
- Takes off to a target altitude
- Detects and aligns with the ArUco marker
- Lands automatically when aligned
- Logs motion metrics for post-mission analysis
