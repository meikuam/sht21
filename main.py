import os
import csv
import time
from datetime import datetime
from src.sht21 import Si7021


if __name__ == "__main__":
    path = "data.csv"
    sensor = Si7021()
    sensor.set_heater_level(3)


    time_interval = 30

    temps = []
    hums = []
    eventtimes = []
    dump_iters = 10
    cur_iter = 0

    while True:
        try:
            eventtime = datetime.now()
            temp = sensor.get_temperature()
            hum = sensor.get_humidity()

            temps.append(temp)
            hums.append(hum)
            eventtimes.append(eventtime)


            if cur_iter >= dump_iters:
                print("dump", len(temps))

                if not os.path.exists(path):
                    write_head = True
                else:
                    write_head = False
                with open(path, 'a+') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=',')
                    if write_head:
                        csv_writer.writerow(["temperature", "humidity", "eventtime"])
                    for t, h, d in zip(temps, hums, eventtimes):
                        csv_writer.writerow([t, h, d])
                    temps = []
                    hums = []
                    eventtimes = []
                    cur_iter = 0
            cur_iter += 1
        except Exception as e:
            print(e)

        time.sleep(time_interval)
