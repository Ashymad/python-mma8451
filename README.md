### python-mma8451

Python library for use with mma8451 accelerometers.
Developed as a part of a [project on AGH UST](https://github.com/Ashymad/OSKA-Pi-MEMS).
Originally based on [massixone/mma8451](https://github.com/massixone/mma8451) but since rewritten and relicensed.

### Example usage:
```Python
from mma8451 import mma8451
import signal
import sys
from datetime import datetime
import h5py as h5

def sigint_handler(signal, frame):
    print('Exiting...')
    MMA8451.close()
    sys.exit(0)

def callback(data):
    dataset = datetime.now().strftime("%Y/%m/%d/%H/%M/%S")
    print("Saving " + dataset)
    with h5.File("data.h5", "a") as f:
        f.create_dataset(dataset, data=data)

MMA8451 = mma8451.Device()
MMA8451.open()
MMA8451.restart()
MMA8451.configure(bit_depth=14,
                  auto_sleep=False,
                  power_mode="high_resolution",
                  sleep_power_mode="high_resolution",
                  fifo_mode="fill",
                  fifo_watermark=20,
                  low_noise=True)

signal.signal(signal.SIGINT, signal.SIG_IGN)
MMA8451.setup_threaded_fifo_callback(gpio_pin=17,
                                     interrupt_pin=1,
                                     callback=callback,
                                     time_interval=30,
                                     convert_to_float=False)

signal.signal(signal.SIGINT, sigint_handler)
print('Finished initialization')
signal.pause()
```
