# generated from genmsg/cmake/pkg-genmsg.cmake.em

message(STATUS "armaction: 7 messages, 0 services")

set(MSG_I_FLAGS "-Iarmaction:/home/jetson/yahboomcar_ws/devel/share/armaction/msg;-Igeometry_msgs:/opt/ros/noetic/share/geometry_msgs/cmake/../msg;-Iactionlib_msgs:/opt/ros/noetic/share/actionlib_msgs/cmake/../msg;-Istd_msgs:/opt/ros/noetic/share/std_msgs/cmake/../msg")

# Find all generators
find_package(gencpp REQUIRED)
find_package(geneus REQUIRED)
find_package(genlisp REQUIRED)
find_package(gennodejs REQUIRED)
find_package(genpy REQUIRED)

add_custom_target(armaction_generate_messages ALL)

# verify that message/service dependencies have not changed since configure



get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg" NAME_WE)
add_custom_target(_armaction_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "armaction" "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg" "armaction/ArmControlActionResult:actionlib_msgs/GoalID:armaction/ArmControlActionGoal:armaction/ArmControlActionFeedback:armaction/ArmControlResult:armaction/ArmControlGoal:std_msgs/Header:armaction/ArmControlFeedback:actionlib_msgs/GoalStatus"
)

get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg" NAME_WE)
add_custom_target(_armaction_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "armaction" "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg" "actionlib_msgs/GoalID:armaction/ArmControlGoal:std_msgs/Header"
)

get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg" NAME_WE)
add_custom_target(_armaction_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "armaction" "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg" "actionlib_msgs/GoalID:armaction/ArmControlResult:actionlib_msgs/GoalStatus:std_msgs/Header"
)

get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg" NAME_WE)
add_custom_target(_armaction_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "armaction" "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg" "actionlib_msgs/GoalID:actionlib_msgs/GoalStatus:std_msgs/Header:armaction/ArmControlFeedback"
)

get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg" NAME_WE)
add_custom_target(_armaction_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "armaction" "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg" ""
)

get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg" NAME_WE)
add_custom_target(_armaction_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "armaction" "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg" ""
)

get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg" NAME_WE)
add_custom_target(_armaction_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "armaction" "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg" ""
)

#
#  langs = gencpp;geneus;genlisp;gennodejs;genpy
#

### Section generating for lang: gencpp
### Generating Messages
_generate_msg_cpp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg"
  "${MSG_I_FLAGS}"
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/armaction
)
_generate_msg_cpp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/armaction
)
_generate_msg_cpp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/armaction
)
_generate_msg_cpp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/armaction
)
_generate_msg_cpp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/armaction
)
_generate_msg_cpp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/armaction
)
_generate_msg_cpp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/armaction
)

### Generating Services

### Generating Module File
_generate_module_cpp(armaction
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/armaction
  "${ALL_GEN_OUTPUT_FILES_cpp}"
)

add_custom_target(armaction_generate_messages_cpp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_cpp}
)
add_dependencies(armaction_generate_messages armaction_generate_messages_cpp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg" NAME_WE)
add_dependencies(armaction_generate_messages_cpp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg" NAME_WE)
add_dependencies(armaction_generate_messages_cpp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg" NAME_WE)
add_dependencies(armaction_generate_messages_cpp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg" NAME_WE)
add_dependencies(armaction_generate_messages_cpp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg" NAME_WE)
add_dependencies(armaction_generate_messages_cpp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg" NAME_WE)
add_dependencies(armaction_generate_messages_cpp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg" NAME_WE)
add_dependencies(armaction_generate_messages_cpp _armaction_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(armaction_gencpp)
add_dependencies(armaction_gencpp armaction_generate_messages_cpp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS armaction_generate_messages_cpp)

### Section generating for lang: geneus
### Generating Messages
_generate_msg_eus(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg"
  "${MSG_I_FLAGS}"
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/armaction
)
_generate_msg_eus(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/armaction
)
_generate_msg_eus(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/armaction
)
_generate_msg_eus(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/armaction
)
_generate_msg_eus(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/armaction
)
_generate_msg_eus(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/armaction
)
_generate_msg_eus(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/armaction
)

### Generating Services

### Generating Module File
_generate_module_eus(armaction
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/armaction
  "${ALL_GEN_OUTPUT_FILES_eus}"
)

add_custom_target(armaction_generate_messages_eus
  DEPENDS ${ALL_GEN_OUTPUT_FILES_eus}
)
add_dependencies(armaction_generate_messages armaction_generate_messages_eus)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg" NAME_WE)
add_dependencies(armaction_generate_messages_eus _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg" NAME_WE)
add_dependencies(armaction_generate_messages_eus _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg" NAME_WE)
add_dependencies(armaction_generate_messages_eus _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg" NAME_WE)
add_dependencies(armaction_generate_messages_eus _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg" NAME_WE)
add_dependencies(armaction_generate_messages_eus _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg" NAME_WE)
add_dependencies(armaction_generate_messages_eus _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg" NAME_WE)
add_dependencies(armaction_generate_messages_eus _armaction_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(armaction_geneus)
add_dependencies(armaction_geneus armaction_generate_messages_eus)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS armaction_generate_messages_eus)

### Section generating for lang: genlisp
### Generating Messages
_generate_msg_lisp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg"
  "${MSG_I_FLAGS}"
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/armaction
)
_generate_msg_lisp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/armaction
)
_generate_msg_lisp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/armaction
)
_generate_msg_lisp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/armaction
)
_generate_msg_lisp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/armaction
)
_generate_msg_lisp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/armaction
)
_generate_msg_lisp(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/armaction
)

### Generating Services

### Generating Module File
_generate_module_lisp(armaction
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/armaction
  "${ALL_GEN_OUTPUT_FILES_lisp}"
)

add_custom_target(armaction_generate_messages_lisp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_lisp}
)
add_dependencies(armaction_generate_messages armaction_generate_messages_lisp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg" NAME_WE)
add_dependencies(armaction_generate_messages_lisp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg" NAME_WE)
add_dependencies(armaction_generate_messages_lisp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg" NAME_WE)
add_dependencies(armaction_generate_messages_lisp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg" NAME_WE)
add_dependencies(armaction_generate_messages_lisp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg" NAME_WE)
add_dependencies(armaction_generate_messages_lisp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg" NAME_WE)
add_dependencies(armaction_generate_messages_lisp _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg" NAME_WE)
add_dependencies(armaction_generate_messages_lisp _armaction_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(armaction_genlisp)
add_dependencies(armaction_genlisp armaction_generate_messages_lisp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS armaction_generate_messages_lisp)

### Section generating for lang: gennodejs
### Generating Messages
_generate_msg_nodejs(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg"
  "${MSG_I_FLAGS}"
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/armaction
)
_generate_msg_nodejs(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/armaction
)
_generate_msg_nodejs(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/armaction
)
_generate_msg_nodejs(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/armaction
)
_generate_msg_nodejs(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/armaction
)
_generate_msg_nodejs(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/armaction
)
_generate_msg_nodejs(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/armaction
)

### Generating Services

### Generating Module File
_generate_module_nodejs(armaction
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/armaction
  "${ALL_GEN_OUTPUT_FILES_nodejs}"
)

add_custom_target(armaction_generate_messages_nodejs
  DEPENDS ${ALL_GEN_OUTPUT_FILES_nodejs}
)
add_dependencies(armaction_generate_messages armaction_generate_messages_nodejs)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg" NAME_WE)
add_dependencies(armaction_generate_messages_nodejs _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg" NAME_WE)
add_dependencies(armaction_generate_messages_nodejs _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg" NAME_WE)
add_dependencies(armaction_generate_messages_nodejs _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg" NAME_WE)
add_dependencies(armaction_generate_messages_nodejs _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg" NAME_WE)
add_dependencies(armaction_generate_messages_nodejs _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg" NAME_WE)
add_dependencies(armaction_generate_messages_nodejs _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg" NAME_WE)
add_dependencies(armaction_generate_messages_nodejs _armaction_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(armaction_gennodejs)
add_dependencies(armaction_gennodejs armaction_generate_messages_nodejs)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS armaction_generate_messages_nodejs)

### Section generating for lang: genpy
### Generating Messages
_generate_msg_py(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg"
  "${MSG_I_FLAGS}"
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/armaction
)
_generate_msg_py(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/armaction
)
_generate_msg_py(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/armaction
)
_generate_msg_py(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/armaction
)
_generate_msg_py(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/armaction
)
_generate_msg_py(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/armaction
)
_generate_msg_py(armaction
  "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/armaction
)

### Generating Services

### Generating Module File
_generate_module_py(armaction
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/armaction
  "${ALL_GEN_OUTPUT_FILES_py}"
)

add_custom_target(armaction_generate_messages_py
  DEPENDS ${ALL_GEN_OUTPUT_FILES_py}
)
add_dependencies(armaction_generate_messages armaction_generate_messages_py)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlAction.msg" NAME_WE)
add_dependencies(armaction_generate_messages_py _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionGoal.msg" NAME_WE)
add_dependencies(armaction_generate_messages_py _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionResult.msg" NAME_WE)
add_dependencies(armaction_generate_messages_py _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlActionFeedback.msg" NAME_WE)
add_dependencies(armaction_generate_messages_py _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlGoal.msg" NAME_WE)
add_dependencies(armaction_generate_messages_py _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlResult.msg" NAME_WE)
add_dependencies(armaction_generate_messages_py _armaction_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/jetson/yahboomcar_ws/devel/share/armaction/msg/ArmControlFeedback.msg" NAME_WE)
add_dependencies(armaction_generate_messages_py _armaction_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(armaction_genpy)
add_dependencies(armaction_genpy armaction_generate_messages_py)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS armaction_generate_messages_py)



if(gencpp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/armaction)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/armaction
    DESTINATION ${gencpp_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_cpp)
  add_dependencies(armaction_generate_messages_cpp geometry_msgs_generate_messages_cpp)
endif()
if(TARGET actionlib_msgs_generate_messages_cpp)
  add_dependencies(armaction_generate_messages_cpp actionlib_msgs_generate_messages_cpp)
endif()

if(geneus_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/armaction)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/armaction
    DESTINATION ${geneus_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_eus)
  add_dependencies(armaction_generate_messages_eus geometry_msgs_generate_messages_eus)
endif()
if(TARGET actionlib_msgs_generate_messages_eus)
  add_dependencies(armaction_generate_messages_eus actionlib_msgs_generate_messages_eus)
endif()

if(genlisp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/armaction)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/armaction
    DESTINATION ${genlisp_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_lisp)
  add_dependencies(armaction_generate_messages_lisp geometry_msgs_generate_messages_lisp)
endif()
if(TARGET actionlib_msgs_generate_messages_lisp)
  add_dependencies(armaction_generate_messages_lisp actionlib_msgs_generate_messages_lisp)
endif()

if(gennodejs_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/armaction)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/armaction
    DESTINATION ${gennodejs_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_nodejs)
  add_dependencies(armaction_generate_messages_nodejs geometry_msgs_generate_messages_nodejs)
endif()
if(TARGET actionlib_msgs_generate_messages_nodejs)
  add_dependencies(armaction_generate_messages_nodejs actionlib_msgs_generate_messages_nodejs)
endif()

if(genpy_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/armaction)
  install(CODE "execute_process(COMMAND \"/usr/bin/python3\" -m compileall \"${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/armaction\")")
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/armaction
    DESTINATION ${genpy_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_py)
  add_dependencies(armaction_generate_messages_py geometry_msgs_generate_messages_py)
endif()
if(TARGET actionlib_msgs_generate_messages_py)
  add_dependencies(armaction_generate_messages_py actionlib_msgs_generate_messages_py)
endif()
