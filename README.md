# SR620PY
## _Remotely control your SR620 Universal Time Interval Counter_

<a href="https://lab3841.it/">
  <img src="https://lab3841.it/wp-content/uploads/logo.svg" 
       alt="Logo" 
       width="150" />
</a>


---
**SR620PY** is a python library designed to perform **measurements** and apply custom **configurations** to a SR620 Universal Time Counter (produced by Stanford Research Systems).

## Features

- Remotely apply a **configuration** to your SR620
- Start a **measure** or a **set of measurements**
- Start an **Allan Variance** set of measurements

## Installation

To use the library, install it by using `pip` command:
```sh
pip install sr620py
```
`sr620py` requires `pyserial` and `tqdm` to work properly.

To upgrade the library:
```sh
pip install sr620py --upgrade
```

## How to use it
To **open a connection** with yout SR620 device, the corresponding **serial port** and **log file** path must be specified:
```python
from sr620py import *

device = SR620('/dev/ttyUSB0','mylogfile.log') #starts the connection
#...your code here...
device.close_connection()
```
If no log file is specified, the output will be written on your standard console.
> As soon as the connection is established, the current configuration of the device is read

### Start a measure
To **start a measure**, you need to specify the type of statistics you want to read. All the **statistics** are saved in constants starting with `STATISTICS_`:
```python
device.measure(STATISTICS_MEAN) #measure the mean
device.measure(STATISTICS_MAX) #measure the maximum
device.measure(STATISTICS_MIN) #measure the minimum
device.measure(STATISTICS_JITTER) #measure the jitter
```
```python
res = device.measure(STATISTICS_MEAN) #measure the mean...
print(res) #...and print the result
```
When a measure is started, a progress bar is shown in console. To disable it:
```python
device.measure(STATISTICS_MEAN,progress=False)
```
### Set of measurements
To start a **set of measurements**, the **number** of measurements and the statistics must be specified:
```python
res = device.start_measurement_set(STATISTICS_JITTER,10) #measure a set of 10 jitters...

for num in res:
    print(num) #...and print the result
```
To save the result in **csv file**, the csv file path must be specified:
```python
device.start_measurement_set(STATISTICS_JITTER,10,file_path='mycsv.csv') #save the result in a csv file
```
To start an **undefinite set of measurements**:
```python
res = device.start_measurement_set_forever(STATISTICS_MEAN,file_path='mycsv.csv')
print(res)
```
To block the measurement set, a Keyboard Interrupt `CTRL+C` command must be sent.
### Allan Variance
sr620py allows to start the measure of the **Allan Variance of a signal** over different number of samples (10,100,1000,...). The result is saved in a **dictionary** with this format:
`{10:value0,100:value1,1000:value2,...}`.
To **start the measurement** of an Allan Variance set, the **number of powers** of ten must be specified:
```python
dct = device.start_measurement_allan_variance(3) #measure the Allan Variance for 10,100,1000 number of samples...
print(dct) #...and print the result
```
Also in this case the result can be saved in a **csv file**:
```python
dct = device.start_measurement_allan_variance(3,file_path='mycsv.csv')
```
To block the measurement set before the end, a Keyboard Interrupt `CTRL+C` command must be sent.
### Apply a custom configuration
sr620py finally allows to **apply a custom configuration** to the device. The complete command to apply the configuration is:
```python
device.set_custom_configuration(
    mode=MODE_FREQUENCY,
    source=SOURCE_A,
    jitter=JITTER_ALLAN,
    arming=ARMING_CENTISECOND,
    size=5,
    clock=CLOCK_EXTERNAL,
    clock_frequency=CLOCK_FREQUENCY_10_MEGAHZ,
)
```
The available options are contained in constants starting with: `MODE_`,`SOURCE_`,`JITTER_`,`ARMING_`,`CLOCK_`,`CLOCK_FREQUENCY_`. The size must be one of the following values: `1,2,5,1e1,2e1,5e1,1e2,2e2,5e2,1e3,2e3,5e3,1e4,2e4,5e4,1e5,2e5,5e5,1e6,2e6,5e6`.

The user can obviously specify **only the options in which is interested in**:
```python
device.set_custom_configuration(
    mode=MODE_COUNT,
    source=SOURCE_B,
) #only change the mode and the source
```
Other methods can also be used in order to **change option singularly**:
```python
device.set_mode(MODE_FREQUENCY) #set mode
device.set_clock_frequency(CLOCK_FREQUENCY_10_MEGAHZ) #set clock frequency
device.set_number_samples(100) #set number of samples
```
> Attention: when a configuration is sent to the device, it's possible that is not actually applied. To check the current configuration, the print option must me added to the methods:

```python
device.set_custom_configuration(
    ...,
    print=True
)
```
The result will be something like that:
```
-------------------------------------
***SR620 parameters configuration***
    Mode: freq
    Source: A
    Arming: 1s
    NumOfSamples: 100.0
    TypeOfJitter: STD
    Clock: int
    ClockFrequency: 10mhz
-------------------------------------
```


## License

MIT License


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
