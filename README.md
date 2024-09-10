# SR620PY
## _Remotely control your SR620 Universal Time Interval Counter_

<a href="https://lab3841.it/">
  <img src="https://lab3841.it/wp-content/uploads/logo.svg" 
       alt="Logo" 
       width="150" />
</a>

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

SR620PY is a python library designed to perform measurements and apply custom configurations to a SR620 Universal Time Counter (Stanford Research Systems).

## Features

- Remotely apply a configuration to your SR620
- Start a measure or a set of measurements
- Start an Allan Variance set of measurements

## Installation

To use the library, install it by using `pip` command
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
To start a measure, you need to specify the type of statistics you want to read. All the statistics are saved in constants starting with `STATISTICS_`:
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
To start a set of measurements, the number of measurements and the statistics must be specified:
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

### Apply a custom configuration

Dillinger is currently extended with the following plugins.
Instructions on how to use them in your own application are linked below.

| Plugin | README |
| ------ | ------ |
| Dropbox | [plugins/dropbox/README.md][PlDb] |
| GitHub | [plugins/github/README.md][PlGh] |
| Google Drive | [plugins/googledrive/README.md][PlGd] |
| OneDrive | [plugins/onedrive/README.md][PlOd] |
| Medium | [plugins/medium/README.md][PlMe] |
| Google Analytics | [plugins/googleanalytics/README.md][PlGa] |

## Development

Want to contribute? Great!

Dillinger uses Gulp + Webpack for fast developing.
Make a change in your file and instantaneously see your updates!

Open your favorite Terminal and run these commands.

First Tab:

```sh
node app
```

Second Tab:

```sh
gulp watch
```

(optional) Third:

```sh
karma test
```

#### Building for source

For production release:

```sh
gulp build --prod
```

Generating pre-built zip archives for distribution:

```sh
gulp build dist --prod
```

## Docker

Dillinger is very easy to install and deploy in a Docker container.

By default, the Docker will expose port 8080, so change this within the
Dockerfile if necessary. When ready, simply use the Dockerfile to
build the image.

```sh
cd dillinger
docker build -t <youruser>/dillinger:${package.json.version} .
```

This will create the dillinger image and pull in the necessary dependencies.
Be sure to swap out `${package.json.version}` with the actual
version of Dillinger.

Once done, run the Docker image and map the port to whatever you wish on
your host. In this example, we simply map port 8000 of the host to
port 8080 of the Docker (or whatever port was exposed in the Dockerfile):

```sh
docker run -d -p 8000:8080 --restart=always --cap-add=SYS_ADMIN --name=dillinger <youruser>/dillinger:${package.json.version}
```

> Note: `--capt-add=SYS-ADMIN` is required for PDF rendering.

Verify the deployment by navigating to your server address in
your preferred browser.

```sh
127.0.0.1:8000
```

## License

MIT

**Free Software, Hell Yeah!**

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
