import time
from periphery import I2C


class Si7021:
    """
    Si7021-A20
    https://ru.mouser.com/datasheet/2/368/Si7021-A20-1397917.pdf
    
    implementation based on:
    https://github.com/adafruit/Adafruit_Si7021

    """
    def __init__(self):
        self.i2c = I2C("/dev/i2c-0")
        self.address = 0x40

        self.TEMP_MEASURE_HOLD = 0xE3
        self.HUMD_MEASURE_HOLD = 0xE5
        self.TEMP_MEASURE_NOHOLD = 0xF3
        self.HUMD_MEASURE_NOHOLD = 0xF5
        self.RESET_CMD = 0xFE

        self.READRHT_REG_CMD = 0xE7
        self.WRITERHT_REG_CMD = 0xE6
        self.REG_HTRE_BIT = 0x2

        self.WRITEHEATER_REG_CMD = 0x51
        self.READHEATER_REG_CMD = 0x11

        self.reset()

    def reset(self):
        self.i2c.transfer(
            self.address,
            [I2C.Message([self.RESET_CMD])]
        )
        time.sleep(0.05)

    def read_RHT(self):
        msgs = [I2C.Message([self.READRHT_REG_CMD]), I2C.Message([0x00], read=True)]
        self.i2c.transfer(self.address, msgs)
        data = msgs[1].data[0]
        return data

    def is_heater_enabled(self):
        data = self.read_RHT()
        data &= (1 << self.REG_HTRE_BIT)
        return data > 0

    def set_heater(self, enable: bool):
        data = self.read_RHT()
        if enable:
            data |= (1 << self.REG_HTRE_BIT)
        else:
            data &= 0xFF ^ (1 << self.REG_HTRE_BIT)
        self.i2c.transfer(
            self.address,
            [I2C.Message([self.WRITERHT_REG_CMD, data])]
        )

    def set_heater_level(self, level: int):
        """level - value from 0 to 15"""
        level &= 0xF
        self.i2c.transfer(
            self.address,
            [I2C.Message([self.WRITEHEATER_REG_CMD, level])]
        )

    def get_heater_level(self):
        msgs = [I2C.Message([self.READHEATER_REG_CMD]), I2C.Message([0x00], read=True)]
        self.i2c.transfer(self.address, msgs)
        return msgs[1].data[0]

    def read_sensor(self, address, bit_length=8):
        data = [0x00] * max(bit_length // 8, 1)
        msgs = [I2C.Message([address]), I2C.Message(data, read=True)]
        self.i2c.transfer(self.address, msgs)
        return msgs[1].data

    def get_temperature(self):
        data = self.read_sensor(self.TEMP_MEASURE_HOLD, 16)
        data = data[0] << 8 | data[1]

        return -46.85 + (175.72 / 65536.0) * data

    def get_humidity(self):
        data = self.read_sensor(self.HUMD_MEASURE_HOLD, 16)
        data = data[0] << 8 | data[1]
        return min(max(-6.0 + (125.0 / 65536.0) * data, 0), 100)


if __name__ == "__main__":
    sensor = Si7021()
    counter = 0
    sensor.set_heater_level(3)
    while True:
        temp = sensor.get_temperature()
        hum = sensor.get_humidity()
        print("temp", round(temp, 2), "hum", round(hum, 2))
        time.sleep(1)
        counter += 1
        if counter >= 10:
            heater_status = sensor.is_heater_enabled()
            sensor.set_heater(not heater_status)
            counter = 0
