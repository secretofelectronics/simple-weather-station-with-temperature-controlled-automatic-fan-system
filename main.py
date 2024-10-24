from machine import Pin, I2C
import ssd1306
import dht
import time

time.sleep(0.5)
# I2C setup for SSD1306 OLED display (GPIO 0 -> SDA, GPIO 1 -> SCL)
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# DHT11 sensor setup (GPIO 2)
dht_sensor = dht.DHT11(Pin(2))

# Push button pins (GPIO 3, 4, 5 for set, increase, decrease)
set_temp_button = Pin(3, Pin.IN, Pin.PULL_DOWN)
inc_button = Pin(4, Pin.IN, Pin.PULL_DOWN)
dec_button = Pin(5, Pin.IN, Pin.PULL_DOWN)

# Fan control pin (GPIO 6)
fan_pin = Pin(6, Pin.OUT)
fan_pin.value(0)  # Fan off by default

# Variables for fan control
set_fan_temp = 25  # Default fan temperature
setting_mode = False
last_button_press_time = 0
TIMEOUT_DURATION = 2  # Timeout in seconds for auto-exit from Set mode

def display_data(temp, humidity):
    """Function to display temperature, humidity, and fan temperature."""
    oled.fill(0)
    oled.text('Temp: {} C'.format(temp), 0, 0)
    oled.text('Humidity: {} %'.format(humidity), 0, 16)
    oled.text('Fan Temp: {} C'.format(set_fan_temp), 0, 32)
    oled.show()

def display_set_mode():
    """Function to display Set Fan Temp mode."""
    oled.fill(0)
    oled.text('Set Fan Temp Mode', 0, 0)
    oled.text('Fan Temp: {}'.format(set_fan_temp), 0, 16)
    oled.show()

def read_dht():
    """Function to read data from the DHT11 sensor."""
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    return temperature, humidity

while True:
    # Read temperature and humidity from DHT11 sensor
    temperature, humidity = read_dht()

    # Check if setting mode is active (toggle with set_temp_button)
    if set_temp_button.value() == 1:
        time.sleep(0.2)  # Debouncing
        setting_mode = not setting_mode  # Toggle mode
        last_button_press_time = time.time()  # Record the time of mode change

    # If in setting mode
    if setting_mode:
        display_set_mode()  # Display the setting mode screen
        
        # Check for user input (increase/decrease buttons)
        if inc_button.value() == 1:  # Increase fan temperature
            set_fan_temp += 1
            last_button_press_time = time.time()  # Reset the timeout timer
            time.sleep(0.2)  # Debouncing

        if dec_button.value() == 1:  # Decrease fan temperature
            set_fan_temp -= 1
            last_button_press_time = time.time()  # Reset the timeout timer
            time.sleep(0.2)  # Debouncing

        # Auto-exit setting mode after TIMEOUT_DURATION if no buttons are pressed
        if time.time() - last_button_press_time > TIMEOUT_DURATION:
            setting_mode = False  # Exit setting mode and save the value

    else:
        # Normal mode: Display temperature, humidity, and fan temperature
        display_data(temperature, humidity)

    # Fan control logic: Turn on if temp >= set temp, off otherwise
    if temperature >= set_fan_temp:
        fan_pin.value(1)  # Turn on the fan
    else:
        fan_pin.value(0)  # Turn off the fan

    # Delay before next sensor reading
    time.sleep(0.5)
