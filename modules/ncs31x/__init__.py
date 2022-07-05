##########
##
##  SPDX-License-Identifier: MIT
##
##  Copyright (c) 2017-2022 James M. Putnam <putnamjm.design@gmail.com>
##
##########

##########
##
## NCS31X device driver
##
###########
"""
"""

import pigpio
from time import struct_time

class Ncs31x:
    """NCS31X class
    """

    """ pin to GPIO translation
          User GPIO 2-27 (0 and 1 are reserved).

          GPIO	pin	pin	GPIO	
    3V3	   -	1	2	-	5V
    SDA	   2	3	4	-	5V
    SCL	   3	5	6	-	Ground
           4	7	8	14	TXD
    Gnd	   -	9	10	15	RXD
    ce1   17	11	12	18	ce0
          27	13	14	-	Gnd
          22    15	16	23	
    3V3	   -    17	18	24	
    MOSI  10	19	20	-	Gnd
    MISO   9	21	22	25	
    SCLK  11	23	24	8	CE0
    Gnd    -	25	26	7	CE1
    ID_SD  0	27	28	1	ID_SC
           5	29	30	-	Gnd
           6	31	32	12	
          13	33	34	-	Gnd
    miso  19	35	36	16	ce2
          26	37	38	20	mosi
    Gnd    -	39	40	21	sclk
    """

    """
    # wiringpi pin constants
    LE_PIN = 3
    R5222_PIN = 22
    
    GREEN_LIGHT_PIN = 27
    RED_LIGHT_PIN = 28
    BLUE_LIGHT_PIN = 29

    BUZZER_PIN = 0
    
    UP_BUTTON_PIN = 1
    DOWN_BUTTON_PIN = 4
    MODE_BUTTON_PIN = 5
    """

    # pigpio pin constants
    LE_PIN = 22
    R5222_PIN = 6
    
    GREEN_LIGHT_PIN = 16
    RED_LIGHT_PIN = 20
    BLUE_LIGHT_PIN = 21

    BUZZER_PIN = 17
    
    UP_BUTTON_PIN = 1
    DOWN_BUTTON_PIN = 4
    MODE_BUTTON_PIN = 5

    I2C_ADDRESS = 0x68
    I2C_FLUSH = 0

    # NCS31X internals
    _DEBOUNCE_DELAY = 150
    _TOTAL_DELAY = 17

    _SECOND_REGISTER = 0x0
    _MINUTE_REGISTER = 0x1
    _HOUR_REGISTER = 0x2
    _WEEK_REGISTER = 0x3
    _DAY_REGISTER = 0x4
    _MONTH_REGISTER = 0x5
    _YEAR_REGISTER = 0x6

    _MAX_POWER = 100

    _UPPER_DOTS_MASK = 0x80000000
    _LOWER_DOTS_MASK = 0x40000000

    _LEFT_REPR_START = 5
    _LEFT_BUFFER_START = 0
    _RIGHT_REPR_START = 2
    _RIGHT_BUFFER_START = 4

    # class variables
    _gpio = None
    _gpio_i2c = None
    _gpio_spi = None
    
    _hv5222 = None
    
    def clear(self):
        self.display([0 for _ in range(8)])
        
    def blank(self):
        """power off the display
        """

        # self.display([0 for _ in range(8)])
        self._gpio.write(self.LE_PIN, 0)

    def unblank(self):
        """power on the display
        """

        self._gpio.write(self.LE_PIN, 1)

    def backlight(self, color):
        """change the backlight color
        """

        # wiringpi.softPwmWrite(self._RED_LIGHT_PIN, color[0])
        # wiringpi.softPwmWrite(self._GREEN_LIGHT_PIN, color[1])
        # wiringpi.softPwmWrite(self._BLUE_LIGHT_PIN, color[2])

    def write_rtc(self, tm):
        """write the RTC from a time struct
        """
        def _dec_to_bcd(val):
            return (int(val / 10) * 16) + (val % 10)

        self._gpio.i2c_write_byte(self._gpio_i2c, self.I2C_FLUSH)
        self._gpio.i2c_write_byte_data(self._gpio_i2c, self._SECOND_REGISTER,
                                       _dec_to_bcd(tm.tm_sec))
        self._gpio.ic2_write_byte_data(self._gpio_i2c, self._MINUTE_REGISTER,
                                      _dec_to_bcd(tm.tm_min))
        self._gpio.ic2_write_byte_data(self._gpio_i2c, self._HOUR_REGISTER,
                                      _dec_to_bcd(tm.tm_hour))
        self._gpio.ic2_write_byte_data(self._gpio_i2c, self._WEEK_REGISTER,
                                      _dec_to_bcd(tm.tm_wday))
        self._gpio.ic2_write_byte_data(self._gpio_i2c, self._DAY_REGISTER,
                                      _dec_to_bcd(tm.tm_mday))
        self._gpio.ic2_write_byte_data(self._gpio_i2c, self._MONTH_REGISTER,
                                      _dec_to_bcd(tm.tm_mon))
        self._gpio.ic2_write_byte_data(self._gpio_i2c, self._YEAR_REGISTER,
                                      _dec_to_bcd(tm.tm_year))
        self._gpio.ic2_write_byte(self._gpio_i2c, self.I2C_FLUSH)

    def read_rtc(self, hour12):
        """read the RTC
            return a struct_time()
        """
        
        def _bcd_to_dec(val):
            return ((val >> 4) * 10) + (val & 0xf)

        def _hour12():
            tm_hour = _bcd_to_dec(self._gpio.i2c_read_byte_data(self._gpio_i2c, self._HOUR_REGISTER))
            if hour12 and tm_hour > 12:
                tm_hour -= 12

            return tm_hour

        self._gpio.i2c_write_byte(self._gpio_i2c, self.I2C_FLUSH)

        now = (_bcd_to_dec(self._gpio.i2c_read_byte_data(self._gpio_i2c, self._YEAR_REGISTER)) + 1900,
               _bcd_to_dec(self._gpio.i2c_read_byte_data(self._gpio_i2c, self._MONTH_REGISTER)),
               _bcd_to_dec(self._gpio.i2c_read_byte_data(self._gpio_i2c, self._DAY_REGISTER)),
               _hour12(),
               _bcd_to_dec(self._gpio.i2c_read_byte_data(self._gpio_i2c, self._MINUTE_REGISTER)),
               _bcd_to_dec(self._gpio.i2c_read_byte_data(self._gpio_i2c, self._SECOND_REGISTER)),
               _bcd_to_dec(self._gpio.i2c_read_byte_data(self._gpio_i2c, self._WEEK_REGISTER)),
               1,
               -1)

        return struct_time(now)

    def display(self, tubes):
        """put the tube representation into the tubes
        """

        def rev_bits(nval):
            reversed_ = 0
            i = 0
            while i < 64:
                if nval & 1 << i:
                    reversed_ |= 1 << (63 - i)

            return reversed_

        def tube_to_bits(tubes):
            bits = 0
            for n in range(8):
                bits |= tubes[n]
                bits <<= 8

            return bits

        def init_pin(self, pin):
            """set a GPIO pin to input and pulled-up
            """

            self._gpio.set_mode(pin, pigpio.INPUT)
            self._gpio.set_pull_up_down(pin, pigpio.PUD_UP)

        def func_mode(self):
            """button debouncing
            """

            if (time.time_ns() - self.func_mode.debounce) > self._DEBOUNCE_DELAY:
                print('MODE button was pressed.')
                self.func_mode.debounce = time.time_ns()

        def func_up(self):
            """button debouncing
            """
            if (time.time_ns() - self.func_up.debounce) > self._DEBOUNCE_DELAY:
                print('UP button was pressed.')
                self.func_up.debounce = time.time_ns()

        def func_down(self):
            """button debouncing
            """

            if (time.time_ns() - self.func_down.debounce) > self._DEBOUNCE_DELAY:
                print('DOWN button was pressed.')
                self.func_down.debounce = time.time_ns()

        func_mode.debounce = 0
        func_up.debounce = 0
        func_down.debounce = 0

        display_ = tubes
        if self._hv5222:
            reverse = rev_bits(tube_to_bits(display_))

            display_[4] = reverse
            display_[5] = reverse >> 8
            display_[6] = reverse >> 16
            display_[7] = reverse >> 24
            display_[0] = reverse >> 32
            display_[1] = reverse >> 40
            display_[2] = reverse >> 48
            display_[3] = reverse >> 56

        self._gpio.spi_write(self._gpio_spi, bytes(display_))

    def __init__(self):
        """initialize an ncs31x object
        """

        self._gpio = pigpio.pi()

        # wiringpi.softToneCreate(BUZZER_PIN)
        # wiringpi.softToneWrite(BUZZER_PIN, 1000)

        # wiringpi.softPwmCreate(self._RED_LIGHT_PIN, 0, self._MAX_POWER)
        # wiringpi.softPwmCreate(self._GREEN_LIGHT_PIN, 0, self._MAX_POWER)
        # wiringpi.softPwmCreate(self._BLUE_LIGHT_PIN, 0, self._MAX_POWER)

        # open the I2C and SPI busses to the NCS31X device
        self._gpio_i2c = self._gpio.i2c_open(1, self.I2C_ADDRESS)
        self._gpio_spi = self._gpio.spi_open(0, 2000000, 2)
        
        # initialize the display
        self._gpio.set_mode(self.LE_PIN, pigpio.OUTPUT)
        self._gpio.set_mode(self.R5222_PIN, pigpio.INPUT)
        self._gpio.set_pull_up_down(self.R5222_PIN, pigpio.PUD_UP)
        self._hv5222 = not self._gpio.read(self.R5222_PIN)

