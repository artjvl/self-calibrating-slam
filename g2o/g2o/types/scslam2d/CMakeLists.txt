add_library(types_scslam2d ${G2O_LIB_TYPE}
        ../slam2d/types_slam2d.h
        ../slam2d/se2.h
        ../slam3d/types_slam3d.h
        utility_poses2d.h utility_poses2d.cpp
        node_v2.h node_v2.cpp
        node_se2.h node_se2.cpp
        param.h param.cpp
        param_v2.h param_v2.cpp
        param_se2.h param_se2.cpp
        info3.h info3.cpp
        constraint_pose2d_se2.h constraint_pose2d_se2.cpp
        constraint_pose2d_v2.h constraint_pose2d_v2.cpp
        constraint_poses2d_se2.h constraint_poses2d_se2.cpp
        constraint_poses2d_se2_pv2.h constraint_poses2d_se2_pv2.cpp
        constraint_poses2d_se2_pse2.h constraint_poses2d_se2_pse2.cpp
        constraint_poses2d_se2_cov.h constraint_poses2d_se2_cov.cpp
)

set_target_properties(types_scslam2d PROPERTIES OUTPUT_NAME ${LIB_PREFIX}types_scslam2d)
if (APPLE)
    set_target_properties(types_scslam2d PROPERTIES INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}")
endif()
target_link_libraries(types_scslam2d core)
if(G2O_HAVE_OPENGL)
    target_link_libraries(types_scslam2d opengl_helper ${OPENGL_gl_LIBRARY} )
endif()

install(TARGETS types_scslam2d
        EXPORT ${G2O_TARGETS_EXPORT_NAME}
        RUNTIME DESTINATION ${RUNTIME_DESTINATION}
        LIBRARY DESTINATION ${LIBRARY_DESTINATION}
        ARCHIVE DESTINATION ${ARCHIVE_DESTINATION}
#        INCLUDES DESTINATION ${INCLUDES_DESTINATION}
)

file(GLOB headers "${CMAKE_CURRENT_SOURCE_DIR}/*.h" "${CMAKE_CURRENT_SOURCE_DIR}/*.hpp")
install(FILES ${headers} DESTINATION ${INCLUDES_INSTALL_DIR}/types/scslam2d)
