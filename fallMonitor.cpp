 
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "edge-impulse-sdk/classifier/ei_run_classifier.h"

#define I2C_PORT i2c0
#define SDA_PIN 0
#define SCL_PIN 1
#define FALL_INPUT 2
#define MPU6050_ADDR 0x68 
#include <stdbool.h> 

// Define the size based on sampling rate
// (50 samples per second * 2 seconds = 100 slots)
#define BUFFER_SIZE 100 

float flattened_data[300]; // global array to hold the flattened data for the classifier (100 samples * 3 axes)

// 1. Structure for a single reading
typedef struct {
    float x;
    float y;
    float z;
} MotionData;

// 2. Structure for the rolling window
typedef struct {
    MotionData readings[BUFFER_SIZE];
    int write_index;
    bool is_full;
} CircularBuffer;
// Function to insert live MPU6050 data into the rolling window
void add_reading(CircularBuffer* buffer, float new_x, float new_y, float new_z) {
    
    // 1. Write the new data into the current available slot
    buffer->readings[buffer->write_index].x = new_x;
    buffer->readings[buffer->write_index].y = new_y;
    buffer->readings[buffer->write_index].z = new_z;
    
    // 2. Move the pointer to the next slot
    buffer->write_index++;
    
    // 3. The Wrap-Around Logic 
    if (buffer->write_index >= BUFFER_SIZE) {
        buffer->write_index = 0;   // Snap back to the beginning
        buffer->is_full = true;    // Flag that we now have a complete history
    }
} 

int get_data_callback(size_t offset, size_t length, float *out_ptr) {
    // We want to fetch 'length' number of samples.
    for (size_t i = 0; i < length; i++) {
        // We look into your circular buffer, starting at the 
        // offset provided by the library, and copy it into the 
        // 'out_ptr' which is the memory address the library provided.
        out_ptr[i] = flattened_data[offset + i]; 
    }
    return 0; 
}

int main() {
    stdio_init_all();
    bool fallIndicator = false; 
    // Initialize I2C hardware
    i2c_init(I2C_PORT, 100 * 1000);
    gpio_set_function(SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(SCL_PIN, GPIO_FUNC_I2C);
    gpio_init(FALL_INPUT);
    gpio_set_dir(FALL_INPUT, GPIO_IN);
    gpio_pull_down(FALL_INPUT);
    gpio_pull_up(SDA_PIN);
    gpio_pull_up(SCL_PIN);

    



    // delay 10 seconds fro human setup (start serial monitor)
    sleep_ms(10000); 
    printf("\n--- Waking up MPU6050 ---\n");

    // wake sensor
    uint8_t wake_command[2] = {0x6B, 0x00};
    i2c_write_blocking(I2C_PORT, MPU6050_ADDR, wake_command, 2, false);
    // define buffer instance
    CircularBuffer fall_buffer;
    fall_buffer.write_index = 0;
    
    fall_buffer.is_full = false;

    printf("Starting Fall Monitor...\n");
  
    while (1) {
        //Prepare to read data from accelerometer
        uint8_t reg = 0x3B; 
        i2c_write_blocking(I2C_PORT, MPU6050_ADDR, &reg, 1, true); 
        
        uint8_t data[6];
        i2c_read_blocking(I2C_PORT, MPU6050_ADDR, data, 6, false);
        
        int16_t accel_x_raw = (data[0] << 8) | data[1];
        int16_t accel_y_raw = (data[2] << 8) | data[3];
        int16_t accel_z_raw = (data[4] << 8) | data[5];

        float accel_x = (accel_x_raw / 16384.0) * 9.81;
        float accel_y = (accel_y_raw / 16384.0) * 9.81;
        float accel_z = (accel_z_raw / 16384.0) * 9.81;

        fallIndicator = gpio_get(FALL_INPUT);

        // Rolling window
        add_reading(&fall_buffer, accel_x, accel_y, accel_z);
        printf("%.2f,%.2f,%.2f, %d\n", accel_x, accel_y, accel_z, fall_buffer.write_index);

        
    
        if (fall_buffer.is_full) {
           
            printf("Buffer Full. Running Classifier...\n");


            for (int i = 0; i < BUFFER_SIZE; i++) {
                flattened_data[i * 3] = fall_buffer.readings[i].x;
                flattened_data[i * 3 + 1] = fall_buffer.readings[i].y;
                flattened_data[i * 3 + 2] = fall_buffer.readings[i].z;
            }
            
            
            // 1. Declare the "manifest"
            signal_t signal;

            // 2. Tell the model how much data total it should expect (50hz * 2 seconds = 100 samples, each with 3 axes = 300)
            signal.total_length = 300;

            // 3. Point the "get_data" pointer to your Librarian function
            signal.get_data = &get_data_callback;

            // 4. Create an empty result container
            ei_impulse_result_t result = { 0 };

            // 5. Run the classifier!
            // The library will now use your 'signal' manifest to 
            // call 'get_data_callback' as many times as it needs.
            int err = run_classifier(&signal, &result, false);

            // 6. Check for errors (Safety Gate)
            if (err != EI_IMPULSE_OK) {
                printf("ERR: Failed to run classifier (%d)\n", err);
            } 
            else {
                // Output the result
                printf("Predictions: Fall: %.2f\n", result.classification[0].value);
                }
            
            fall_buffer.is_full = false; // reset the buffer full flag to start filling again
            }

                // Control the Sampling Rate (50Hz)
                sleep_ms(20); 
    }
}