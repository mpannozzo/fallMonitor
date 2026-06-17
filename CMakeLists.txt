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
# 3. Add your executable (Named "app" internally so Edge Impulse is happy)
add_executable(app fallMonitor.cpp )

# But tell the Pico SDK to output the final file as "fallMonitor.uf2"
pico_set_program_name(app "fallMonitor")
pico_set_program_version(app "0.1")

# Enable USB output, disable UART on the "app" target
pico_enable_stdio_uart(app 0)
pico_enable_stdio_usb(app 1)

# 4. Inject Edge Impulse SDK (it will automatically look for and attach to "app")
include(edge-impulse-sdk/cmake/utils.cmake)
add_subdirectory(edge-impulse-sdk/cmake/zephyr)
RECURSIVE_FIND_FILE_APPEND(MODEL_SOURCE "tflite-model" "*.cpp")

# Link our local files to the "app" target
target_include_directories(app PRIVATE .)
target_sources(app PRIVATE ${MODEL_SOURCE})

# 5. Consolidated Linker (Standard Pico + Hardware + EI)
target_link_libraries(app
        pico_stdlib
        hardware_i2c
        hardware_timer
)

# Tell Pico to generate the .uf2 and .hex files for "app"
pico_add_extra_outputs(app)