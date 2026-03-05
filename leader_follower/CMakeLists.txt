cmake_minimum_required(VERSION 3.8)
project(leader_follower)

# Find dependencies
find_package(ament_cmake REQUIRED)

# Install
# C++ source, include, and library build logic removed since teleop is handled by leader_follower_py.
install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})

# Export dependencies
ament_package()
