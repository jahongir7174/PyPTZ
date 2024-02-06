import time

from bs4 import BeautifulSoup
from requests import auth, get


class VAPIXCamera:
    """
    Module for controlling AXIS cameras using VAPIX
    """

    def __init__(self, ip, user, password):
        self.__username = user
        self.__password = password
        self.__url = 'http://' + ip + '/axis-cgi/com/ptz.cgi'

    @staticmethod
    def __merge(*args) -> dict:
        """
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts

        Args:
            *args: argument dictionary

        Returns:
            Return a merged dictionary
        """
        results = {}
        for dictionary in args:
            results.update(dictionary)
        return results

    def __cmd(self, payload: dict):
        """
        Function used to send commands to the camera
        Args:
            payload: argument dictionary for camera control

        Returns:
            Returns the response from the device to the command sent
        """

        args = {'camera': 1, 'html': 'no', 'timestamp': int(time.time())}

        response = get(self.__url,
                       auth=auth.HTTPDigestAuth(self.__username, self.__password),
                       params=VAPIXCamera.__merge(payload, args))

        if (response.status_code != 200) and (response.status_code != 204):
            soup = BeautifulSoup(response.text, features="lxml")
            print('%s', soup.get_text())
            if response.status_code == 401:
                exit(1)

        return response

    def absolute_move(self, pan: float, tilt: float, zoom: int, speed: int):
        """
        Operation to move pan, tilt or zoom to a absolute destination.

        Args:
            pan: pans the device relative to the (0,0) position.
            tilt: tilts the device relative to the (0,0) position.
            zoom: zooms the device n steps.
            speed: speed move camera.

        Returns:
            Returns the response from the device to the command sent.
        """
        return self.__cmd({'pan': pan, 'tilt': tilt, 'zoom': zoom, 'speed': speed})

    def continuous_move(self, pan: int, tilt: int, zoom: int):
        """
        Operation for continuous Pan/Tilt and Zoom movements.

        Args:
            pan: speed of movement of Pan.
            tilt: speed of movement of Tilt.
            zoom: speed of movement of Zoom.

        Returns:
            Returns the response from the device to the command sent.

        """
        pan_tilt = str(pan) + "," + str(tilt)
        return self.__cmd({'continuouspantiltmove': pan_tilt, 'continuouszoommove': zoom})

    def relative_move(self, pan: float, tilt: float, zoom: int, speed: int):
        """
        Operation for Relative Pan/Tilt and Zoom Move.

        Args:
            pan: pans the device n degrees relative to the current position.
            tilt: tilts the device n degrees relative to the current position.
            zoom: zooms the device n steps relative to the current position.
            speed: speed move camera.

        Returns:
            Returns the response from the device to the command sent.
        """
        return self.__cmd({'rpan': pan, 'rtilt': tilt, 'rzoom': zoom, 'speed': speed})

    def stop_move(self):
        """
        Operation to stop ongoing pan, tilt and zoom movements of absolute relative and
        continuous type

        Returns:
            Returns the response from the device to the command sent
        """
        return self.__cmd({'continuouspantiltmove': '0,0', 'continuouszoommove': 0})

    def center_move(self, pos_x: int, pos_y: int, speed: int):
        """
        Used to send the coordinates for the point in the image where the user clicked.
        This information is then used by the server to calculate the pan/tilt move required to
        (approximately) center the clicked point.

        Args:
            pos_x: value of the X coordinate.
            pos_y: value of the Y coordinate.
            speed: speed move camera.

        Returns:
            Returns the response from the device to the command sent
        """
        pan_tilt = str(pos_x) + "," + str(pos_y)
        return self.__cmd({'center': pan_tilt, 'speed': speed})

    def area_zoom(self, pos_x: int, pos_y: int, zoom: int, speed: int):
        """
        Centers on positions x,y (like the center command) and zooms by a factor of z/100.

        Args:
            pos_x: value of the X coordinate.
            pos_y: value of the Y coordinate.
            zoom: zooms by a factor.
            speed: speed move camera.

        Returns:
            Returns the response from the device to the command sent
        """
        x_y_zoom = str(pos_x) + "," + str(pos_y) + "," + str(zoom)
        return self.__cmd({'areazoom': x_y_zoom, 'speed': speed})

    def move(self, position: str, speed: float):
        """
        Moves the device 5 degrees in the specified direction.

        Args:
            position: position to move. (home, up, down, left, right, up-left, up-right, down-left...)
            speed: speed move camera.

        Returns:
            Returns the response from the device to the command sent
        """
        return self.__cmd({'move': str(position), 'speed': speed})

    def go_home_position(self, speed: int):
        """
        Operation to move the PTZ device to it's "home" position.

        Args:
            speed: speed move camera.

        Returns:
            Returns the response from the device to the command sent
        """
        return self.__cmd({'move': 'home', 'speed': speed})

    def get_ptz_status(self):
        """
        Operation to request PTZ status.

        Returns:
            Returns a tuple with the position of the camera (P, T, Z)
        """
        response = self.__cmd({'query': 'position'})
        pan = float(response.text.split()[0].split('=')[1])
        tilt = float(response.text.split()[1].split('=')[1])
        zoom = float(response.text.split()[2].split('=')[1])

        return pan, tilt, zoom

    def go_to_server_preset_name(self, name: str, speed: int):
        """
        Move to the position associated with the preset on server.

        Args:
            name: name of preset position server.
            speed: speed move camera.

        Returns:
            Returns the response from the device to the command sent
        """
        return self.__cmd({'gotoserverpresetname': name, 'speed': speed})

    def go_to_server_preset_number(self, number: int, speed: int):
        """
        Move to the position associated with the specified preset position number.

        Args:
            number: number of preset position server.
            speed: speed move camera.

        Returns:
            Returns the response from the device to the command sent
        """
        return self.__cmd({'gotoserverpresetno': number, 'speed': speed})

    def go_to_device_preset(self, preset_pos: int, speed: int):
        """
        Bypasses the preset pos interface and tells the device to go directly to the preset
        position number stored in the device, where is a device-specific preset position number.

        Args:
            preset_pos: number of preset position device
            speed: speed move camera

        Returns:
            Returns the response from the device to the command sent

        """
        return self.__cmd({'gotodevicepreset': preset_pos, 'speed': speed})

    def list_preset_device(self):
        """
        List the presets positions stored in the device.

        Returns:
            Returns the list of presets positions stored on the device.

        """
        return self.__cmd({'query': 'presetposcam'})

    def list_all_preset(self):
        """
        List all available presets position.

        Returns:
            Returns the list of all presets positions.

        """
        response = self.__cmd({'query': 'presetposall'})
        soup = BeautifulSoup(response.text, features="lxml")
        resp_presets = soup.text.split('\n')
        presets = []

        for i in range(1, len(resp_presets) - 1):
            preset = resp_presets[i].split("=")
            presets.append((int(preset[0].split('presetposno')[1]), preset[1].rstrip('\r')))

        return presets

    def set_speed(self, speed: int = None):
        """
        Sets the head speed of the device that is connected to the specified camera.
        Args:
            speed: speed value.

        Returns:
            Returns the response from the device to the command sent.

        """
        return self.__cmd({'speed': speed})

    def get_speed(self):
        """
        Requests the camera's speed of movement.

        Returns:
            Returns the camera's move value.

        """
        resp = self.__cmd({'query': 'speed'})
        return int(resp.text.split()[0].split('=')[1])

    def info_ptz_command(self):
        """
        Returns a description of available PTZ commands. No PTZ control is performed.

        Returns:
            Success (OK and system log content text) or Failure (error and description).

        """
        return self.__cmd({'info': '1'}).text
