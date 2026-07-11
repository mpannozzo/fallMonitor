cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# == DO NOT EDIT THE FOLLOWING LINES for the Raspberry Pi Pico VS Code Extension to work ==
if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.2.0)
set(toolchainVersion 14_2_Rel1)
set(picotoolVersion 2.2.0-a4)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()
# ====================================================================================
set(PICO_BOARD pico CACHE STRING "Board type")

# 1. Pull in Raspberry Pi Pico SDK (MUST be before project)
include(pico_sdk_import.cmake)

project(fallMonitor C CXX ASM)

# 2. Initialise the Raspberry Pi Pico SDK
pico_sdk_init()

# ---------------------------------------------------------
# 3. Build the Edge Impulse SDK + trained model ONCE as a static library.
#    This replaces the old "inject sources straight into a target named app"
#    approach so that multiple executables can share the same model code.
# ---------------------------------------------------------
include(edge-impulse-sdk/cmake/utils.cmake)

# Gather Edge Impulse SDK sources (mirrors edge-impulse-sdk/cmake/zephyr/CMakeLists.txt)
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk" "*.cpp")
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk" "*.cc")
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk" "*.s")
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk/CMSIS/DSP/Source/TransformFunctions" "*.c")
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk/CMSIS/DSP/Source/CommonTables" "*.c")
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk/CMSIS/DSP/Source/BasicMathFunctions" "*.c")
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk/CMSIS/DSP/Source/ComplexMathFunctions" "*.c")
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk/CMSIS/DSP/Source/FastMathFunctions" "*.c")
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk/CMSIS/DSP/Source/SupportFunctions" "*.c")
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk/CMSIS/DSP/Source/MatrixFunctions" "*.c")
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk/CMSIS/DSP/Source/StatisticsFunctions" "*.c")
RECURSIVE_FIND_FILE_APPEND(EI_SOURCE_FILES "edge-impulse-sdk/CMSIS/NN/Source" "*.c")
LIST(APPEND EI_SOURCE_FILES "edge-impulse-sdk/tensorflow/lite/c/common.c")

# Gather the exported trained model sources
RECURSIVE_FIND_FILE_APPEND(MODEL_SOURCE "tflite-model" "*.cpp")

add_library(edge_impulse STATIC ${EI_SOURCE_FILES} ${MODEL_SOURCE})

# Expose include paths to anything that links this library.
# ".": lets code use "edge-impulse-sdk/...", "tflite-model/...", "model-parameters/..."
# "edge-impulse-sdk": lets the SDK use its internal "tensorflow/...", "CMSIS/..." includes
target_include_directories(edge_impulse PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}
        ${CMAKE_CURRENT_LIST_DIR}/edge-impulse-sdk
)
target_link_libraries(edge_impulse PUBLIC pico_stdlib)

# ---------------------------------------------------------
# Helper to configure a firmware executable and emit its .uf2
# ---------------------------------------------------------
function(add_firmware_target target_name source_file)
    add_executable(${target_name} ${source_file})
    pico_set_program_name(${target_name} "${target_name}")
    pico_set_program_version(${target_name} "0.1")

    # USB serial on, UART off
    pico_enable_stdio_uart(${target_name} 0)
    pico_enable_stdio_usb(${target_name} 1)

    target_include_directories(${target_name} PRIVATE ${CMAKE_CURRENT_LIST_DIR})
    target_link_libraries(${target_name}
            edge_impulse
            pico_stdlib
            hardware_i2c
            hardware_timer
    )

    # Generate .uf2 / .hex / etc.
    pico_add_extra_outputs(${target_name})
endfunction()

# ---------------------------------------------------------
# 4. Firmware targets (each produces its own .uf2)
# ---------------------------------------------------------
# Data collection / testing build  -> dataCollection.uf2
add_firmware_target(dataCollection dataCollection.cpp)

# Inference / final product build  -> inference.uf2
add_firmware_target(inference inference.cpp)
