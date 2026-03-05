import os
from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node, PushRosNamespace
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    leader_follower_share = FindPackageShare('leader_follower')
    
    leader_xacro_file = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ", PathJoinSubstitution([FindPackageShare('leaderarm_description'), "urdf", "leaderarm.xacro"]),
    ])

    leader_controllers = PathJoinSubstitution([leader_follower_share, "config", "leader_controllers.yaml"])

    return LaunchDescription([
        GroupAction(
            actions=[
                PushRosNamespace('leader'),
                Node(
                    package="controller_manager",
                    executable="ros2_control_node",
                    parameters=[{'robot_description': leader_xacro_file}, leader_controllers],
                    output='screen',
                    remappings=[('/reconnect_event', '/reconnect_event')],
                ),
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["joint_state_broadcaster", "--controller-manager", "/leader/controller_manager"],
                ),
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["leader_effort_controller", "--controller-manager", "/leader/controller_manager"],
                ),
                Node(
                    package='joint_state_publisher',
                    executable='joint_state_publisher',
                    name='leader_jsp',
                    parameters=[{'robot_description': leader_xacro_file}, {'source_list': ['/leader/joint_states_corrected']}],
                    remappings=[('joint_states', 'joint_states_viz')]
                ),
                Node(
                    package='robot_state_publisher',
                    executable='robot_state_publisher',
                    name='leader_state_publisher',
                    output='screen',
                    parameters=[{'robot_description': leader_xacro_file}],
                    remappings=[('joint_states', 'joint_states_viz')]
                ),
            ]
        ),
        # Static TF for Leader position
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0.5', '0', '0', '0', '0', 'world', 'leader_base_link']
        )
    ])