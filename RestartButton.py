import os
import time
import RPi.GPIO as GPIO

# Version: 0.1

def restart():
    os.system('sudo reboot')

def shutdown():
    os.system('sudo shutdown -h now')


# Load Settings
SETTINGS_FILE_PATH = '/home/pi/MeowX/SETTINGS.txt'
with open(SETTINGS_FILE_PATH, 'r') as f:
    for settings_line_raw in f:

        settings_line = settings_line_raw.strip('\n')

        if not settings_line:
            continue

        if settings_line.startswith('#'):
            continue

        variable_part, the_rest = settings_line.split('=')

        if the_rest.startswith("'"):
            # The rest is a string, read until the next '
            value_part = ''
            for char in the_rest[1:]:
                if char == "'":
                    break
                value_part += char
        else:
            # The rest is an integer or boolean and may have a comment at the end.  Split at the first space, if there is one
            if ' ' in the_rest:
                value_part = the_rest.split(' ')[0]
            else:
                # No space or comments, the_rest is a value (int or boolean)
                value_part = the_rest



        if variable_part == 'BUTTON_PIN':
            BUTTON_PIN = int(value_part)
            break

################################################################################

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


CHECK_DELAY = .25  # Polling in seconds
RESTART_TRIGGER_SECONDS = 2
SHUTDOWN_TRIGGER_SECONDS = 5

print ('Restart Button script beginning... [Pin: {}, Check delay: {}s, Restart trigger: {}s, Shutdown trigger: {}s]'.format(BUTTON_PIN, CHECK_DELAY, RESTART_TRIGGER_SECONDS, SHUTDOWN_TRIGGER_SECONDS))

button_down = False
button_down_start_time = time.time()
while True:
    if GPIO.input(BUTTON_PIN) == 0:  # Triggers low due to pull up
        if not button_down:
            # Button pushed
            button_down_start_time = time.time()
            button_down = True
            print ('Button down')
        else:
            # Button currently down, shutdown when time if not released
            button_down_duration = time.time() - button_down_start_time
            if button_down_duration >= SHUTDOWN_TRIGGER_SECONDS:
                print ('Shutting down...')
                shutdown()
                break

    else:
        if button_down:
            # Button released
            button_down = False
            button_down_duration = time.time() - button_down_start_time

            if button_down_duration < RESTART_TRIGGER_SECONDS:
                print ('Button held for less than {} seconds, ignoring'.format(RESTART_TRIGGER_SECONDS))
            elif button_down_duration < SHUTDOWN_TRIGGER_SECONDS:
                print ('Restarting...')
                restart()
            else:
                print ('Shutting down...')
                shutdown()


    time.sleep(CHECK_DELAY)