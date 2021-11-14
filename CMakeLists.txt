cmake_minimum_required(VERSION 3.10)
project(animassist)

message(STATUS "havok sdk root local=${HAVOK_SDK_ROOT}")
message(STATUS "havok sdk root env=$ENV{HAVOK_SDK_ROOT}")

set(
        PROJ_LIBRARIES
        hkCompat.lib
        hkBase.lib
        hkSerialize.lib
        hkSceneData.lib
        hkVisualize.lib
        hkInternal.lib
        hkImageUtilities.lib
        hkaAnimation.lib
        hkaInternal.lib
        hkaPhysics2012Bridge.lib
        hkcdCollide.lib
        hkcdInternal.lib
        hkGeometryUtilities.lib
)

include_directories(
        "$ENV{HAVOK_SDK_ROOT}/Source/"
)

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    link_directories("$ENV{HAVOK_SDK_ROOT}/Lib/win32_vs2012_win7_noSimd/debug/")
else()
    link_directories("$ENV{HAVOK_SDK_ROOT}/Lib/win32_vs2012_win7_noSimd/release/")
endif()

add_definitions(-DUNICODE -D_UNICODE)
add_executable(animassist main.cpp)
target_link_libraries(animassist ${PROJ_LIBRARIES})

set(CMAKE_CXX_STANDARD 14)