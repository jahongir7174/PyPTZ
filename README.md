# PTZ Camera Control using Python

This library is designed to control PTZ cameras using the ONVIF, VAPIX and SUNAPI.

**ONVIF (Open Network Video Interface Forum)** is a global and open industry forum with the goal of facilitating the
development and use of a global open standard for the interface of physical IP-based security products.
ONVIF creates a standard for how IP products within video surveillance and other physical security areas can communicate
with each other.
ONVIF is an organization started in 2008 by Axis Communications, Bosch Security Systems and Sony.

**VAPIX®** is Axis Camera API.

**SUNAPI®** is Hanwha Camera API.

## Installation

````
pip install pyptz
````

## ONVIF

```python
from pyptz.onvif_control import ONVIFCamera

onvif_camera = ONVIFCamera('192.168.1.100', '88', 'admin', 'password')
pan, tilt, zoom = onvif_camera.get_ptz_status()
print(pan, tilt, zoom)
```

## VAPIX

```python
from pyptz.vapix_control import VAPIXCamera

vapix_camera = VAPIXCamera('192.168.1.100', 'admin', 'password')
pan, tilt, zoom = vapix_camera.get_ptz_status()
print(pan, tilt, zoom)
```

## SUNAPI

```python
from pyptz.sunapi_control import SUNAPICamera

sunapi_camera = SUNAPICamera('192.168.1.100', 'admin', 'password')
pan, tilt, zoom = sunapi_camera.get_ptz_status()[:3]
print(pan, tilt, zoom)
```
