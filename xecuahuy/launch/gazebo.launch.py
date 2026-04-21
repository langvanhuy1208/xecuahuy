import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'xecuahuy'
    pkg_share = get_package_share_directory(pkg_name)
    
    # Đường dẫn tới file URDF
    urdf_file = os.path.join(pkg_share, 'urdf', 'xecuahuy.urdf')
    
    # --- THÊM DÒNG NÀY: Đường dẫn tới file cấu hình RViz ---
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'config.rviz')
    
    # Đường dẫn tới Gazebo ROS
    gazebo_ros_dir = get_package_share_directory('gazebo_ros')

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # 1. Node Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True  
        }]
    )

    # 2. Joint State Publisher GUI
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # 3. Khởi động Gazebo (Server và Client)
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros_dir, 'launch', 'gzserver.launch.py'))
    )
    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros_dir, 'launch', 'gzclient.launch.py'))
    )

    # 4. Node Spawn Robot vào Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'xecuahuy', '-z', '0.1'],
        output='screen'
    )

    # 5. Khởi động RViz2 (Đã cập nhật để tự load file config)
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        # --- THÊM DÒNG NÀY: Đối số -d để load file cấu hình ---
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}] 
    )

    return LaunchDescription([
        gazebo_server,
        gazebo_client,
        robot_state_publisher,
        joint_state_publisher_gui,
        spawn_entity,
        rviz2
    ])
