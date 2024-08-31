# WebDriverPy

**WebDriverPy** is an extended version of the Chromium based Chrome WebDriver class provided by [*Selenium*](https://www.selenium.dev).

It mainly aims to make the WebDriver more accessible in terms of [required setup](https://selenium-python.readthedocs.io/installation.html) to run it, and therefore automates the necessary installations, along with optional ones, such as an [ad blocker extension](https://ublockorigin.com).


## Installation

1. Clone the git repository
    ```shell
    git clone https://github.com/DarthRevan333/WebDriverPy
    ```

2. Install required dependencies (also listed [here](requirements.txt))
    ```shell
    pip install selenium requests
    ```

Any additional dependencies, such as the [Chromedriver or Chrome binaries](https://googlechromelabs.github.io/chrome-for-testing/), are automatically downloaded to the package's directory on first usage.

The [*WebDriver* class](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L38) can also be used to manage these additional dependencies.

## Usage

### Package Usage

Inside the cloned git repository, [a folder called " WebDriverPy"](WebDriverPy) is the actual Python package, from which one can import all functionality.

One *cannot* import from the [outer WebDriverPy folder](.) (containing *[LICENSE](LICENSE)*, *[README.md](README.md)*, [etc.](.))

Imports are only allowed from the inner [WebDriverPy folder](WebDriverPy) containing the [\_\_init\_\_.py](WebDriverPy/__init__.py) file.

The primary class this entire Project is centered around is the [WebDriver class](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L38), which is mainly be configured via the constructor ([documentation here](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L76)) and then also provides a variety of other methods to use like [find()](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L728), [click()](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L865), [wait_until()](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L789), [combinations of those](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L915), [fullscreen()](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L976), [prevent_fullscreen()](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L981), [capture_screen()](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L1021), [etc.](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L45) 

### [Examples](main.py)

Inside the cloned [*outer* WebDriverPy folder:](.)
```Python
from WebDriverPy import WebDriver

WebDriver(no_cookies=True) \
    .get("https://google.com") \
    .wait_click_write_submit("Hello World!", "q", by="name") \
    .wait_for_user_input() \
    .quit()
```

***Result***: Opens [Google](https://google.com), waits for the search bar to load, enters "Hello World!" and submits the search query. Finally it waits for an User input to quit the driver.

### [DriverScripts](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver_scripts.py#L8)

There are also [DriverScripts](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver_scripts.py#L8) in [driver_scripts.py](WebDriverPy/driver_scripts.py), which offer an easy way of nicely encapsulating scripts controlling the browser to perform certain actions. The file also includes some [predefined scripts](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver_scripts.py#L71).

**Example**:
```Python
from WebDriverPy import WebDriver, OpenGoogle

driver = WebDriver(no_cookies=True)

OpenGoogle(driver).run() \
    .wait_for_user_input() \
    .quit()
```

***Result***: Executes the [OpenGoogle script](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver_scripts.py#L71), which opens [Google](https://google.com) and waits for the search bar to load, then waits for user input to finally quit the driver.

To define a custom [DriverScript](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver_scripts.py#L8), simply inherit from the [DriverScript class](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver_scripts.py#L8) and override the run method. Check [the documentation of driver_scripts.py](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver_scripts.py#L16) for more information

## Package Structure

The [*inner* WebDriverPy folder](WebDriverPy) contains or may create the following folders at runtime (they are all created automatically if not present in the [package folder](WebDriverPy)):

- [***captures***](WebDriverPy/captures): Default directory to store screen recordings until they are moved elsewhere 
- [***chrome_binary***](WebDriverPy/chrome_binary): Default directory to hold the installed chrome binaries
- [***extensions***](WebDriverPy/extensions): Default directory to hold Chrome extensions such as uBlockOrigin or the custom extension used to inject code in Order to make authenticated proxies work.
- [***logs***](WebDriverPy/logs): Default directory to store the driver_logs.txt log file
- [***scripts***](WebDriverPy/scripts): Default directory to store Javascript files, which may be used to enable certain functionality like [capturing the screen](WebDriverPy/scripts/preciseMediaRecorder.js)
- [***temp***](WebDriverPy/temp): Default temporary directory used to hold temporary files, such as .zip files during downloads of other components
- [***subpackages***](WebDriverPy/subpackages): Contains other packages used by the [WebDriver](https://github.com/DarthRevan333/WebDriverPy/blob/main/WebDriverPy/driver.py#L38), such as the [PyProxies package](https://github.com/DarthRevan333/PyProxies) used for scraping free proxies if requested by the User.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.