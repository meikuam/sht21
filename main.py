import os
import pandas as pd
from datetime import datetime
from src.sht21 import Si7021


if __name__ == "__main__":
    path = "data.csv"
    sensor = Si7021()
    sensor.set_heater_level(3)



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
                data = pd.DataFrame({
                    "temperature": temps,
                    "humidity": hums,
                    "eventtime": eventtimes
                })
                data.to_csv(
                    path,
                    mode="a" if os.path.exist(path) else "w",
                    header=not os.path.exist(path),
                    index=False
                )
            cur_iter += 1
        except Exception as e:
            pass

        time.sleep(1)
