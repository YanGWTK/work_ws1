# generated from catkin/cmake/template/pkgConfig.cmake.in

# append elements to a list and remove existing duplicates from the list
# copied from catkin/cmake/list_append_deduplicate.cmake to keep pkgConfig
# self contained
macro(_list_append_deduplicate listname)
  if(NOT "${ARGN}" STREQUAL "")
    if(${listname})
      list(REMOVE_ITEM ${listname} ${ARGN})
    endif()
    list(APPEND ${listname} ${ARGN})
  endif()
endmacro()

# append elements to a list if they are not already in the list
# copied from catkin/cmake/list_append_unique.cmake to keep pkgConfig
# self contained
macro(_list_append_unique listname)
  foreach(_item ${ARGN})
    list(FIND ${listname} ${_item} _index)
    if(_index EQUAL -1)
      list(APPEND ${listname} ${_item})
    endif()
  endforeach()
endmacro()

# pack a list of libraries with optional build configuration keywords
# copied from catkin/cmake/catkin_libraries.cmake to keep pkgConfig
# self contained
macro(_pack_libraries_with_build_configuration VAR)
  set(${VAR} "")
  set(_argn ${ARGN})
  list(LENGTH _argn _count)
  set(_index 0)
  while(${_index} LESS ${_count})
    list(GET _argn ${_index} lib)
    if("${lib}" MATCHES "^(debug|optimized|general)$")
      math(EXPR _index "${_index} + 1")
      if(${_index} EQUAL ${_count})
        message(FATAL_ERROR "_pack_libraries_with_build_configuration() the list of libraries '${ARGN}' ends with '${lib}' which is a build configuration keyword and must be followed by a library")
      endif()
      list(GET _argn ${_index} library)
      list(APPEND ${VAR} "${lib}${CATKIN_BUILD_CONFIGURATION_KEYWORD_SEPARATOR}${library}")
    else()
      list(APPEND ${VAR} "${lib}")
    endif()
    math(EXPR _index "${_index} + 1")
  endwhile()
endmacro()

# unpack a list of libraries with optional build configuration keyword prefixes
# copied from catkin/cmake/catkin_libraries.cmake to keep pkgConfig
# self contained
macro(_unpack_libraries_with_build_configuration VAR)
  set(${VAR} "")
  foreach(lib ${ARGN})
    string(REGEX REPLACE "^(debug|optimized|general)${CATKIN_BUILD_CONFIGURATION_KEYWORD_SEPARATOR}(.+)$" "\\1;\\2" lib "${lib}")
    list(APPEND ${VAR} "${lib}")
  endforeach()
endmacro()


if(yahboomcar_astra_CONFIG_INCLUDED)
  return()
endif()
set(yahboomcar_astra_CONFIG_INCLUDED TRUE)

# set variables for source/devel/install prefixes
if("TRUE" STREQUAL "TRUE")
  set(yahboomcar_astra_SOURCE_PREFIX /home/jetson/yahboomcar_ws/src/yahboomcar_astra)
  set(yahboomcar_astra_DEVEL_PREFIX /home/jetson/yahboomcar_ws/devel)
  set(yahboomcar_astra_INSTALL_PREFIX "")
  set(yahboomcar_astra_PREFIX ${yahboomcar_astra_DEVEL_PREFIX})
else()
  set(yahboomcar_astra_SOURCE_PREFIX "")
  set(yahboomcar_astra_DEVEL_PREFIX "")
  set(yahboomcar_astra_INSTALL_PREFIX /home/jetson/yahboomcar_ws/install)
  set(yahboomcar_astra_PREFIX ${yahboomcar_astra_INSTALL_PREFIX})
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "WARNING: package 'yahboomcar_astra' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  message("${_msg}")
endif()

# flag project as catkin-based to distinguish if a find_package()-ed project is a catkin project
set(yahboomcar_astra_FOUND_CATKIN_PROJECT TRUE)

if(NOT "/home/jetson/yahboomcar_ws/devel/include;/usr/include/opencv4 " STREQUAL " ")
  set(yahboomcar_astra_INCLUDE_DIRS "")
  set(_include_dirs "/home/jetson/yahboomcar_ws/devel/include;/usr/include/opencv4")
  if(NOT " " STREQUAL " ")
    set(_report "Check the issue tracker '' and consider creating a ticket if the problem has not been reported yet.")
  elseif(NOT " " STREQUAL " ")
    set(_report "Check the website '' for information and consider reporting the problem.")
  else()
    set(_report "Report the problem to the maintainer 'yahboom <yahboom@todo.todo>' and request to fix the problem.")
  endif()
  foreach(idir ${_include_dirs})
    if(IS_ABSOLUTE ${idir} AND IS_DIRECTORY ${idir})
      set(include ${idir})
    elseif("${idir} " STREQUAL "include ")
      get_filename_component(include "${yahboomcar_astra_DIR}/../../../include" ABSOLUTE)
      if(NOT IS_DIRECTORY ${include})
        message(FATAL_ERROR "Project 'yahboomcar_astra' specifies '${idir}' as an include dir, which is not found.  It does not exist in '${include}'.  ${_report}")
      endif()
    else()
      message(FATAL_ERROR "Project 'yahboomcar_astra' specifies '${idir}' as an include dir, which is not found.  It does neither exist as an absolute directory nor in '/home/jetson/yahboomcar_ws/src/yahboomcar_astra/${idir}'.  ${_report}")
    endif()
    _list_append_unique(yahboomcar_astra_INCLUDE_DIRS ${include})
  endforeach()
endif()

set(libraries "/usr/lib/aarch64-linux-gnu/libopencv_calib3d.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_core.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_dnn.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_features2d.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_flann.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_highgui.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_imgcodecs.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_imgproc.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_ml.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_objdetect.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_photo.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_stitching.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_video.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_videoio.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_aruco.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_bgsegm.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_bioinspired.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_ccalib.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_datasets.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_dnn_objdetect.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_dnn_superres.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_dpm.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_face.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_freetype.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_fuzzy.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_hdf.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_hfs.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_img_hash.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_line_descriptor.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_optflow.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_phase_unwrapping.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_plot.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_quality.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_reg.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_rgbd.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_saliency.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_shape.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_stereo.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_structured_light.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_superres.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_surface_matching.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_text.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_tracking.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_videostab.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_viz.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_ximgproc.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_xobjdetect.so.4.2.0;/usr/lib/aarch64-linux-gnu/libopencv_xphoto.so.4.2.0")
foreach(library ${libraries})
  # keep build configuration keywords, generator expressions, target names, and absolute libraries as-is
  if("${library}" MATCHES "^(debug|optimized|general)$")
    list(APPEND yahboomcar_astra_LIBRARIES ${library})
  elseif(${library} MATCHES "^-l")
    list(APPEND yahboomcar_astra_LIBRARIES ${library})
  elseif(${library} MATCHES "^-")
    # This is a linker flag/option (like -pthread)
    # There's no standard variable for these, so create an interface library to hold it
    if(NOT yahboomcar_astra_NUM_DUMMY_TARGETS)
      set(yahboomcar_astra_NUM_DUMMY_TARGETS 0)
    endif()
    # Make sure the target name is unique
    set(interface_target_name "catkin::yahboomcar_astra::wrapped-linker-option${yahboomcar_astra_NUM_DUMMY_TARGETS}")
    while(TARGET "${interface_target_name}")
      math(EXPR yahboomcar_astra_NUM_DUMMY_TARGETS "${yahboomcar_astra_NUM_DUMMY_TARGETS}+1")
      set(interface_target_name "catkin::yahboomcar_astra::wrapped-linker-option${yahboomcar_astra_NUM_DUMMY_TARGETS}")
    endwhile()
    add_library("${interface_target_name}" INTERFACE IMPORTED)
    if("${CMAKE_VERSION}" VERSION_LESS "3.13.0")
      set_property(
        TARGET
        "${interface_target_name}"
        APPEND PROPERTY
        INTERFACE_LINK_LIBRARIES "${library}")
    else()
      target_link_options("${interface_target_name}" INTERFACE "${library}")
    endif()
    list(APPEND yahboomcar_astra_LIBRARIES "${interface_target_name}")
  elseif(${library} MATCHES "^\\$<")
    list(APPEND yahboomcar_astra_LIBRARIES ${library})
  elseif(TARGET ${library})
    list(APPEND yahboomcar_astra_LIBRARIES ${library})
  elseif(IS_ABSOLUTE ${library})
    list(APPEND yahboomcar_astra_LIBRARIES ${library})
  else()
    set(lib_path "")
    set(lib "${library}-NOTFOUND")
    # since the path where the library is found is returned we have to iterate over the paths manually
    foreach(path /home/jetson/yahboomcar_ws/devel/lib;/home/jetson/software/laser_app/devel/lib;/home/jetson/software/carto_ws/devel_isolated/cartographer_rviz/lib;/home/jetson/software/carto_ws/install_isolated/lib;/home/jetson/software/ar_track_ws/devel/lib;/home/jetson/software/rtabmap_ws/devel/lib;/home/jetson/software/library_ws/devel/lib;/home/jetson/yahboomcar_ws/devel/lib;/opt/ros/noetic/lib)
      find_library(lib ${library}
        PATHS ${path}
        NO_DEFAULT_PATH NO_CMAKE_FIND_ROOT_PATH)
      if(lib)
        set(lib_path ${path})
        break()
      endif()
    endforeach()
    if(lib)
      _list_append_unique(yahboomcar_astra_LIBRARY_DIRS ${lib_path})
      list(APPEND yahboomcar_astra_LIBRARIES ${lib})
    else()
      # as a fall back for non-catkin libraries try to search globally
      find_library(lib ${library})
      if(NOT lib)
        message(FATAL_ERROR "Project '${PROJECT_NAME}' tried to find library '${library}'.  The library is neither a target nor built/installed properly.  Did you compile project 'yahboomcar_astra'?  Did you find_package() it before the subdirectory containing its code is included?")
      endif()
      list(APPEND yahboomcar_astra_LIBRARIES ${lib})
    endif()
  endif()
endforeach()

set(yahboomcar_astra_EXPORTED_TARGETS "yahboomcar_astra_gencfg")
# create dummy targets for exported code generation targets to make life of users easier
foreach(t ${yahboomcar_astra_EXPORTED_TARGETS})
  if(NOT TARGET ${t})
    add_custom_target(${t})
  endif()
endforeach()

set(depends "")
foreach(depend ${depends})
  string(REPLACE " " ";" depend_list ${depend})
  # the package name of the dependency must be kept in a unique variable so that it is not overwritten in recursive calls
  list(GET depend_list 0 yahboomcar_astra_dep)
  list(LENGTH depend_list count)
  if(${count} EQUAL 1)
    # simple dependencies must only be find_package()-ed once
    if(NOT ${yahboomcar_astra_dep}_FOUND)
      find_package(${yahboomcar_astra_dep} REQUIRED NO_MODULE)
    endif()
  else()
    # dependencies with components must be find_package()-ed again
    list(REMOVE_AT depend_list 0)
    find_package(${yahboomcar_astra_dep} REQUIRED NO_MODULE ${depend_list})
  endif()
  _list_append_unique(yahboomcar_astra_INCLUDE_DIRS ${${yahboomcar_astra_dep}_INCLUDE_DIRS})

  # merge build configuration keywords with library names to correctly deduplicate
  _pack_libraries_with_build_configuration(yahboomcar_astra_LIBRARIES ${yahboomcar_astra_LIBRARIES})
  _pack_libraries_with_build_configuration(_libraries ${${yahboomcar_astra_dep}_LIBRARIES})
  _list_append_deduplicate(yahboomcar_astra_LIBRARIES ${_libraries})
  # undo build configuration keyword merging after deduplication
  _unpack_libraries_with_build_configuration(yahboomcar_astra_LIBRARIES ${yahboomcar_astra_LIBRARIES})

  _list_append_unique(yahboomcar_astra_LIBRARY_DIRS ${${yahboomcar_astra_dep}_LIBRARY_DIRS})
  _list_append_deduplicate(yahboomcar_astra_EXPORTED_TARGETS ${${yahboomcar_astra_dep}_EXPORTED_TARGETS})
endforeach()

set(pkg_cfg_extras "")
foreach(extra ${pkg_cfg_extras})
  if(NOT IS_ABSOLUTE ${extra})
    set(extra ${yahboomcar_astra_DIR}/${extra})
  endif()
  include(${extra})
endforeach()
