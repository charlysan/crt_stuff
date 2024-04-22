# Copyright (c) 2024 charlysan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pigpio
import time 
import sys

class VCTi2c(object):
    SDA_GPIO_PIN = 2
    SCL_GPIO_PIN = 3
    FAI_GPIO_PIN = 17
    I2C_SPEED = 40000

    GPIO_HIGH = 1
    GPIO_LOW = 0

    DELAY_START_TRANSACTION = 0.50
    DELAY_END_TRANSACTION = 0.2
    DELAY_READ_BYTE = 0.00

    DDP_ADDR = 0x5E

    # XDFP_WRITE_ADDR = 0XF0
    # XDFP_READ_ADDR = 0XF1
    # XDFP_WRITE_DATA = 0XF2
    # XDFP_READ_DATA = 0XF3
    # XDFP_STATUS = 0XF4
    # 20 ms delay 

    def __init__(
        self,
        SDA=SDA_GPIO_PIN,
        SCL=SCL_GPIO_PIN,
        FA1=FAI_GPIO_PIN,
        I2C_SPEED = I2C_SPEED,
    ):
        self.SDA = SDA 
        self.SCL = SCL
        self.FA1 = FA1
        self.I2C_SPEED = I2C_SPEED

        # Initialize gpio
        self.gpio = pigpio.pi()

        # Set input pullups
        self.gpio.set_pull_up_down(self.FA1, pigpio.PUD_UP)
        self.gpio.set_pull_up_down(self.SDA, pigpio.PUD_UP)
        self.gpio.set_pull_up_down(self.SCL, pigpio.PUD_UP)

        # i2c pins as input by default
        self.gpio.set_mode(self.SDA, pigpio.INPUT)
        self.gpio.set_mode(self.SCL, pigpio.INPUT)

    def __del__(self):
        # close i2c handler
        try:
            self.gpio.bb_i2c_close(self.SDA)
        except Exception as e:
            pass
        try:
            self.gpio.stop()
        except Exception as e:
            pass

    def start_transaction(self, delay=DELAY_START_TRANSACTION):
        r"""Inhibit Master by pulling FA1 down"""  
        self.gpio.write(self.FA1, self.GPIO_LOW)
        time.sleep(delay)

    def end_transaction(self, delay=DELAY_END_TRANSACTION):
        r"""Release Master by pulling FA1 up"""  
        time.sleep(delay)
        self.gpio.write(self.FA1, self.GPIO_HIGH)

    def read_byte_from_RAM_page(self, addr, offset):
        self.gpio.bb_i2c_open(self.SDA, self.SCL, self.I2C_SPEED)
        while True:
            if self.gpio.read(self.SDA) == 1 and self.gpio.read(self.SCL) == 1:
                cmd = [4, addr, 2, 7, 1, offset, 3]
                (count, data) = self.gpio.bb_i2c_zip(self.SDA, cmd)

                time.sleep(self.DELAY_READ_BYTE)

                cmd = [4, addr, 2, 6, 1, 3, 0]
                (count, data) = self.gpio.bb_i2c_zip(self.SDA, cmd)
                self.gpio.bb_i2c_close(self.SDA)
                return data

    def write_byte_into_RAM_page(self, addr, offset, data):
        self.gpio.bb_i2c_open(self.SDA, self.SCL, self.I2C_SPEED)
        cmd = [4, addr, 2, 7, 2, offset, data, 3, 0]
        (count, data) = self.gpio.bb_i2c_zip(self.SDA, cmd)
        self.gpio.bb_i2c_close(self.SDA)

        return data
    
    def read_block_from_RAM_page(self, addr, offset_start, offset_end):
        data = []
        for offset in range(offset_start, offset_end + 1):
            value = self.read_byte_from_RAM_page(addr, offset)
            data.append(value)
        
        return data


    def read_block_from_RAM(
        self, 
        addr_start, 
        addr_end, 
    ):
        data = []
        for page in range(addr_start, addr_end + 1):
            page_data = self.read_block_from_RAM_page(page, 0x00, 0xFF)
            data.append(page_data)
            time.sleep(0.02)

        return data

    def write_DDP_reg(self, sub_addr, hbyte, lbyte):
        self.gpio.bb_i2c_open(self.SDA, self.SCL, self.I2C_SPEED)
        cmd = [4, self.DDP_ADDR, 2, 7, 3, sub_addr, hbyte, lbyte, 3, 0]
        (count, data) = self.gpio.bb_i2c_zip(self.SDA, cmd)
        self.gpio.bb_i2c_close(self.SDA)

        return data


def bytearray_to_hex(raw_data):
    return ' '.join(['0x{:02X}'.format(byte) for byte in raw_data])
        
