add_library(types_sclam2d ${G2O_LIB_TYPE}
        edge_se2_sensor_calib.h edge_se2_sensor_calib.cpp
        vertex_odom_differential_params.h vertex_odom_differential_params.cpp
        edge_se2_odom_differential_calib.h edge_se2_odom_differential_calib.cpp
        odometry_measurement.h odometry_measurement.cpp

        node_se2.h
        node_v1.h node_v1.cpp
        node_v2.h
        node_v3.h

        parameter_util.h
        parameter.h parameter.cpp
        parameter_se2.h parameter_se2.cpp
        parameter_v1.h parameter_v1.cpp
        parameter_v2.h parameter_v2.cpp
        parameter_v3.h parameter_v3.cpp

        constraint_pose2d_v2.h
        constraint_poses2d_se2.h
        constraint_poses2d_se2_se2.h constraint_poses2d_se2_se2.cpp
        constraint_poses2d_se2_v1.h constraint_poses2d_se2_v1.cpp
        constraint_poses2d_se2_v2.h constraint_poses2d_se2_v2.cpp
        constraint_poses2d_se2_v3.h constraint_poses2d_se2_v3.cpp

        info3.h
        constraint_info3.h constraint_info3.cpp
        constraint_poses2d_se2_i.h constraint_poses2d_se2_i.cpp

        types_sclam2d.h types_sclam2d.cpp
        g2o_types_sclam2d_api.h
        )

set_target_properties(types_sclam2d PROPERTIES OUTPUT_NAME ${LIB_PREFIX}types_sclam2d)
if (APPLE)
  set_target_properties(types_sclam2d PROPERTIES INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}")
endif()
target_link_libraries(types_sclam2d types_slam2d types_slam3d core)
if(G2O_HAVE_OPENGL)
  target_link_libraries(types_sclam2d ${OPENGL_gl_LIBRARY})
endif()

install(TARGETS types_sclam2d
  EXPORT ${G2O_TARGETS_EXPORT_NAME}
  RUNTIME DESTINATION ${RUNTIME_DESTINATION}
  LIBRARY DESTINATION ${LIBRARY_DESTINATION}
  ARCHIVE DESTINATION ${ARCHIVE_DESTINATION}
)

file(GLOB headers "${CMAKE_CURRENT_SOURCE_DIR}/*.h" "${CMAKE_CURRENT_SOURCE_DIR}/*.hpp")
install(FILES ${headers} DESTINATION ${INCLUDES_INSTALL_DIR}/types/sclam2d)
