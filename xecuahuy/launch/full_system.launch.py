import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'xecuahuy'
    pkg_share = get_package_share_directory(pkg_name)
    
    # Đường dẫn tới file URDF và RViz
    urdf_file = os.path.join(pkg_share, 'urdf', 'xecuahuy.urdf')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'config.rviz')
    gazebo_ros_dir = get_package_share_directory('gazebo_ros')
    
    # 1. Lấy đường dẫn môi trường TurtleBot3 World
    tb3_world_path = os.path.join(
        get_package_share_directory('turtlebot3_gazebo'),
        'worlds',
        'turtlebot3_world.world'
    )

    # Đọc và xử lý nội dung file URDF để máy khác cũng dùng được
    with open(urdf_file, 'r') as infp:
        robot_desc_raw = infp.read()
    
    # Tự động dịch $(find xecuahuy) thành đường dẫn thực tế trên máy
    robot_desc = robot_desc_raw.replace('$(find xecuahuy)', pkg_share)

    # Node Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True  
        }]
    )

    # 2. Khởi động Gazebo Server
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros_dir, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': tb3_world_path}.items()
    )

    # Khởi động Gazebo Client
    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros_dir, 'launch', 'gzclient.launch.py'))
    )

    # 3. Node Spawn Robot
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'xecuahuy', '-z', '0.1'],
        output='screen'
    )

    # 4. Khởi động RViz2
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}] 
    )

    # 5. CÁC BỘ ĐIỀU KHIỂN (CONTROLLERS)
    load_jsb = TimerAction(
        period=3.0,
        actions=[Node(package="controller_manager", executable="spawner", arguments=["joint_state_broadcaster"])]
    )

    load_diff_drive = TimerAction(
        period=5.0,
        actions=[Node(package="controller_manager", executable="spawner", arguments=["diff_drive_controller"])]
    )

    load_arm = TimerAction(
        period=7.0,
        actions=[Node(package="controller_manager", executable="spawner", arguments=["arm_controller"])]
    )

    # 6. THÊM NODE ĐIỀU KHIỂN CÂN BẰNG
    balancing_script_path = os.path.join(pkg_share, 'scripts', 'balancing_node.py')
    
    load_balancing_node = TimerAction(
        period=9.0,
        actions=[
            Node(
                package=pkg_name,
                executable='/usr/bin/python3', 
                arguments=[balancing_script_path],
                output='screen',
                parameters=[{'use_sim_time': True}]
            )
        ]
    )

    return LaunchDescription([
        gazebo_server,
        gazebo_client,
        robot_state_publisher,
        spawn_entity,
        rviz2,
        load_jsb,
        load_diff_drive,
        load_arm,
        load_balancing_node 
    ])
