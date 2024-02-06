from bs4 import BeautifulSoup
from requests import auth, get


class SUNAPICamera:
    """
    Module for the control of HANWHA cameras using SUNAPI
    """

    def __init__(self, ip, user, password):
        self.__username = user
        self.__password = password
        self.__url = 'http://' + ip + '/stw-cgi/'

    def __cmd(self, cgi: str, payload: dict):
        """
        Function used to send commands to the camera
        Args:
            payload: argument dictionary for camera control

        Returns:
            Returns the response from the device to the command sent
        """

        response = get(self.__url + cgi,
                       auth=auth.HTTPDigestAuth(self.__username, self.__password),
                       params=payload)

        if (response.status_code != 200) and (response.status_code != 204):
            soup = BeautifulSoup(response.text, features="lxml")
            print('%s', soup.get_text())
            if response.status_code == 401:
                exit(1)

        return response

    def get_ptz_status(self):
        """
        Operation to request PTZ status.

        Returns:
            Returns status and notifies when the operation is finished
        """
        response = self.__cmd(cgi='ptzcontrol.cgi',
                              payload={'msubmenu': 'query', 'action': 'view', 'Query': 'Pan,Tilt,Zoom'})

        current_pan = float(response.text.split()[0].split('=')[1])
        current_tilt = float(response.text.split()[1].split('=')[1])
        current_zoom = float(response.text.split()[2].split('=')[1])
        current_zoom_pulse = float(response.text.split()[3].split('=')[1])

        if abs(360 - current_pan) < 0.02 or current_pan < 0.02:
            # This if statement is necessary for when absolute pan is zero.
            # When the camera position is requested, the query returned was either approximately 360 or zero.
            # This statement sets out to fix that bug by forcing the current pan position to be read as zero.
            current_pan = 0

        return current_pan, current_tilt, current_zoom, current_zoom_pulse

    def stop(self):
        """
        Operation to stop ongoing pan, tilt and zoom movements of absolute relative and continuous type

        Returns:
            Returns the response from the device to the command sent
        """

        response = self.__cmd(cgi='ptzcontrol.cgi',
                              payload={'msubmenu': 'stop', 'action': 'control', 'OperationType': 'All'})

        return response

    def absolute_move(self, pan: float, tilt: float, zoom: float):
        """
        Operation to move pan, tilt or zoom to an absolute destination.

        Args:
            pan: pans the device relative to the (0,0) position.
            tilt: tilts the device relative to the (0,0) position.
            zoom: zooms the device n steps relative to 1 zoom.

        Returns:
            Returns the response from the device to the command sent.
        """

        response = self.__cmd(cgi='ptzcontrol.cgi',
                              payload={'msubmenu': 'absolute', 'action': 'control',
                                       'Pan': pan, 'Tilt': tilt, 'Zoom': zoom,
                                       'ZoomPulse': None, 'Channel': None})
        return response

    def relative_move(self, pan: float, tilt: float, zoom: int):
        """
        Operation for Relative Pan/Tilt and Zoom Move.

        Args:
            pan: pans the device n degrees relative to the current position.
            tilt: tilts the device n degrees relative to the current position.
            zoom: zooms the device n steps relative to the current position.

        Returns:
            Returns the response from the device to the command sent.
        """

        current_pan, current_tilt, current_zoom = self.get_ptz_status()[:3]

        if pan is not None:

            # If the relative pan given causes the absolute pan position to surpass 360 degrees,
            # set pan to go the other direction to reach the same location

            if (current_pan + pan) > 360:
                pan = pan - 360

            # If the relative pan given causes the absolute pan position to fall below 0 degrees,
            # set pan to go the other direction to reach the same location

            elif (current_pan + pan) < 0:
                pan = 360 + pan

        if tilt is not None:

            # if the relative tilt given exceeds the 90 degree threshold, set the relative tilt
            # equal to the difference that will result in the maximum 90-degree tilt

            if 90 < (current_tilt + tilt):
                tilt = 90 - current_tilt

            # if the relative tilt given exceeds the -20 degree threshold, set the relative tilt
            # equal to the difference that will result in the minimum -20-degree tilt

            elif (current_tilt + tilt) < -20:
                tilt = -20 + abs(current_tilt)

        if zoom is not None:

            # if the relative zoom given exceeds the 40 zoom threshold, set the relative zoom
            # equal to the difference that will result in the maximum 40 zoom

            if 40 < (current_zoom + zoom):
                zoom = 40 - current_zoom

            # if the relative zoom given exceeds the 1 degree threshold, set the relative zoom
            # equal the difference that will result in the minimum -20-degree tilt

            elif (current_zoom + zoom) < 1:
                zoom = 1 - current_zoom

        if current_pan != 0:
            response = self.__cmd(cgi='ptzcontrol.cgi',
                                  payload={'msubmenu': 'relative', 'action': 'control',
                                           'Pan': pan, 'Tilt': tilt, 'Zoom': zoom,
                                           'ZoomPulse': None, 'Channel': None})

        else:
            response = self.__cmd(cgi='ptzcontrol.cgi',
                                  payload={'msubmenu': 'absolute', 'action': 'control',
                                           'Pan': pan, 'Tilt': tilt, 'Zoom': zoom,
                                           'ZoomPulse': None, 'Channel': None})
        return response

    def continuous_move(self, normalized_speed: bool, pan: int, tilt: int, zoom: int, focus: str):
        """
        Operation for continuous Pan/Tilt and Zoom movements.

        Args:
            normalized_speed: enables or disables the normalized speed range for pan, tilt, zoom.
            pan: speed of movement of Pan.
            tilt: speed of movement of Tilt.
            zoom: speed of movement of Zoom.
            focus: focus control. This parameter cannot be sent together with pan, tilt, or zoom.

        Returns:
            Returns the response from the device to the command sent.
        """

        if focus not in ("Near", "Far", "Stop", None):
            raise Exception("Unauthorized command: Please enter a string from the choices: 'Near', 'Far', or 'Stop'")

        return self.__cmd(cgi='ptzcontrol.cgi',
                          payload={'msubmenu': 'continuous', 'action': 'control',
                                   'NormalizedSpeed': normalized_speed, 'Pan': pan,
                                   'Tilt': tilt, 'Zoom': zoom, 'Focus': focus})

    def area_zoom(self, x1: int, y1: int, x2: int, y2: int, tile_width: int, tile_height: int):
        """
        Centers on positions x,y (like the center command) and zooms by a factor of z/100.

        Args:
            x1: value of the x1 coordinate.
            y1: value of the y1 coordinate.
            x2: value of the x2 coordinate.
            y2: value of the y2 coordinate.
            tile_width: sets tile pixel width
            tile_height: sets tile pixel height

        Returns:
            Returns the response from the device to the command sent
        """

        response = self.__cmd(cgi='ptzcontrol.cgi',
                              payload={'msubmenu': 'areazoom', 'action': 'control',
                                       'X1': x1, 'X2': x2, 'Y1': y1, 'Y2': y2, 'TileWidth': tile_width,
                                       'TileHeight': tile_height})
        return response

    def movement_control(self, direction: str, speed: float):
        """
        Moves the device continuously in the specified direction.

        Args:
            direction: direction to move. (home, up, down, left, right, up-left, upright, down-left...)
            speed: speed to move camera.

        Returns:
            Returns the response from the device to the command sent
        """

        return self.__cmd(cgi='ptzcontrol.cgi',
                          payload={'msubmenu': 'move', 'action': 'control',
                                   'Direction': direction, 'MoveSpeed': speed})

    def go_to_home_position(self, channel: int):
        """
        Operation to move the PTZ device to its "home" position.

        Args:
            channel: returns to home position for provided channel

        Returns:
            Returns the response from the device to the command sent
        """
        return self.__cmd(cgi='ptzcontrol.cgi',
                          payload={'msubmenu': 'home', 'action': 'control', 'Channel': channel})

    def go_to_preset_position(self, preset, preset_name: str):
        """
        Move to the position associated with the preset on server.

        Args:
            preset: numbered position of preset
            preset_name: name of preset position server.
            * cannot be sent together

        Returns:
            Returns the response from the device to the command sent
        """
        return self.__cmd(cgi='ptzcontrol.cgi',
                          payload={'msubmenu': 'preset', 'action': 'control',
                                   'Preset': preset, 'PresetName': preset_name})

    def zoom_out(self):
        """
        Zoom Out to 1x

        Returns:
            Returns the response from the device to the command sent
        """

        response = self.__cmd(cgi='ptzcontrol.cgi',
                              payload={'msubmenu': 'areazoom', 'action': 'control', 'Type': '1x'})
        return response

    def aux_control(self, command: str):
        """
        Execute aux action

        Args:
            command = choice between WiperOn, HeaterOn, HeaterOff

        Returns:
            Returns the response from the device to the command sent
           """

        return self.__cmd(cgi='ptzcontrol.cgi',
                          payload={'msubmenu': 'aux', 'action': 'control', 'Command': command})

    def attributes_information(self):
        """
        create url link to attributes information

        Returns:
            Returns the response from the device to the command sent
        """

        return self.__cmd(cgi='attributes.cgi', payload={})

    def swing_control(self, channel: int, mode: str):
        """
        Move from one preset to another

        Args:
            channel = choose channel
            mode = select mode of either: "Pan", "Tilt", "PanTilt", "Stop"

        Returns:
            Returns the response from the device to the command sent
        """

        if mode not in ("Pan", "Tilt", "PanTilt", "Stop", None):
            raise Exception("Unauthorized command: "
                            "Please enter a string from the choices: 'Pan', 'Tilt', 'PanTilt', 'Stop'")

        return self.__cmd(cgi='ptzcontrol.cgi',
                          payload={'msubmenu': 'swing', 'action': 'control',
                                   'Channel': channel, 'Mode': mode})

    def group_control(self, channel: int, group: int, mode: str):
        """
        Starts and stops a Group operation in which various presets are grouped and called in sequence.

        Args:
            channel = choose channel
            group = select a group sequence set in channel
            mode = choose a mode of either "Start" or "Stop"

        Returns:
            Returns the response from the device to the command sent
        """

        if mode not in ("Start", "Stop", None):
            raise Exception("Unauthorized command: "
                            "Please enter a string from the choices: 'Start' or 'Stop'")

        return self.__cmd(cgi='ptzcontrol.cgi',
                          payload={'msubmenu': 'group', 'action': 'control',
                                   'Channel': channel, 'Group': group,
                                   'Mode': mode})

    def tour_control(self, channel: int, tour: int, mode: str):
        """
        Starts and stops a Tour operation, calling groups of presets in sequence.

        Args:
            channel = choose channel
            tour = select a tour sequence set in channel
            mode = choose a mode of either "Start" or "Stop"

        Returns:
            Returns the response from the device to the command sent
        """

        if mode not in ("Start", "Stop", None):
            raise Exception("Unauthorized command: Please enter a string from the choices: 'Start' or 'Stop'")

        return self.__cmd(cgi='ptzcontrol.cgi',
                          payload={'msubmenu': 'tour', 'action': 'control',
                                   'Channel': channel, 'Tour': tour,
                                   'Mode': mode})

    def trace_control(self, channel: int, trace: int, mode: str):
        """
        Starts and stops a Trace operation

        Args:
            channel = choose channel
            trace = select a trace action that has been set in channel
            mode = choose a mode of either "Start" or "Stop"

        Returns:
            Returns the response from the device to the command sent
        """

        if mode not in ("Start", "Stop", None):
            raise Exception("Unauthorized command: Please enter a string from the choices: 'Start' or 'Stop'")

        return self.__cmd(cgi='ptzcontrol.cgi',
                          payload={'msubmenu': 'trace', 'action': 'control',
                                   'Channel': channel, 'Trace': trace,
                                   'Mode': mode})

    def applications(self):
        """
        Creates url and shares installed applications information
        Returns:
            Returns the response from the device to the command sent
        """

        return self.__cmd(cgi='opensdk.cgi', payload={'msubmenu': 'apps', 'action': 'view'})

    def snap_shot(self):
        """
        Sends snapshot command to the camera
        Returns:
             Returns PIL.Image or None
        """

        response = self.__cmd(cgi='video.cgi',
                              payload={'msubmenu': 'snapshot', 'action': 'view'})

        if response.status_code == 200:
            from io import BytesIO
            from PIL import Image
            return Image.open(BytesIO(response.content))
        else:
            return None
