import onvif


class ONVIFCamera:
    """
    Module for controlling cameras using ONVIF
    """

    def __init__(self, ip, port, username, password):
        camera = onvif.ONVIFCamera(ip, port, username, password)

        ptz = camera.create_ptz_service()
        media = camera.create_media_service()

        self.__ptz = ptz
        self.__token = media.GetProfiles()[0]

    def absolute_move(self, pan: float, tilt: float, zoom: float):
        """
        Operation to move pan, tilt or zoom to an absolute destination.

        Args:
            pan: Pans the device relative to the (0,0) position.
            tilt: Tilts the device relative to the (0,0) position.
            zoom: Zooms the device n steps.

        Returns:
            Return onvif's response
        """
        request = self.__ptz.create_type('AbsoluteMove')
        request.ProfileToken = self.__token
        request.Position = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': zoom}
        response = self.__ptz.AbsoluteMove(request)
        return response

    def continuous_move(self, pan: float, tilt: float, zoom: float):
        """
        Operation for continuous Pan/Tilt and Zoom movements.

        Args:
            pan: speed of movement of Pan.
            tilt: speed of movement of Tilt.
            zoom: speed of movement of Zoom.

        Returns:
            Return onvif's response.
        """
        request = self.__ptz.create_type('ContinuousMove')
        request.ProfileToken = self.__token
        request.Velocity = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': zoom}
        response = self.__ptz.ContinuousMove(request)
        return response

    def relative_move(self, pan: float, tilt: float, zoom: float):
        """
        Operation for Relative Pan/Tilt and Zoom Move.

        Args:
            pan: A positional Translation relative to the pan current position.
            tilt: A positional Translation relative to the tilt current position.
            zoom:

        Returns:
            Return onvif's response
        """
        request = self.__ptz.create_type('RelativeMove')
        request.ProfileToken = self.__token
        request.Translation = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': zoom}
        response = self.__ptz.RelativeMove(request)
        return response

    def stop_move(self):
        """
        Operation to stop ongoing pan, tilt and zoom movements of absolute relative and continuous type.

        Returns:
            Return onvif's response
        """
        request = self.__ptz.create_type('Stop')
        request.ProfileToken = self.__token
        response = self.__ptz.Stop(request)
        return response

    def set_home_position(self):
        """
        Operation to save current position as the home position.

        Returns:
            Return onvif's response
        """
        request = self.__ptz.create_type('SetHomePosition')
        request.ProfileToken = self.__token
        response = self.__ptz.SetHomePosition(request)
        self.__ptz.Stop({'ProfileToken': self.__token})
        return response

    def go_home_position(self):
        """
        Operation to move the PTZ device to it's "home" position.

        Returns:
            Return onvif's response
        """
        request = self.__ptz.create_type('GotoHomePosition')
        request.ProfileToken = self.__token
        response = self.__ptz.GotoHomePosition(request)
        return response

    def get_ptz_status(self):
        """
        Operation to request PTZ status.

        Returns:
            Returns a list with the values of Pan, Tilt and Zoom
        """
        request = self.__ptz.create_type('GetStatus')
        request.ProfileToken = self.__token
        ptz_status = self.__ptz.GetStatus(request)
        pan = ptz_status.Position.PanTilt.x
        tilt = ptz_status.Position.PanTilt.y
        zoom = ptz_status.Position.Zoom.x
        return pan, tilt, zoom

    def set_preset(self, preset_name: str):
        """
        The command saves the current device position parameters.
        Args:
            preset_name: Name for preset.

        Returns:
            Return onvif's response.
        """
        presets = ONVIFCamera.get_preset_complete(self)
        request = self.__ptz.create_type('SetPreset')
        request.ProfileToken = self.__token
        request.PresetName = preset_name

        for i, preset in enumerate(presets):
            if str(presets[i].Name) == preset_name:
                return None

        ptz_set_preset = self.__ptz.SetPreset(request)
        return ptz_set_preset

    def get_preset(self):
        """
        Operation to request all PTZ presets.

        Returns:
            Returns a list of tuples with the presets.
        """
        ptz_get_presets = ONVIFCamera.get_preset_complete(self)

        presets = []
        for i, _ in enumerate(ptz_get_presets):
            presets.append((i, ptz_get_presets[i].Name))
        return presets

    def get_preset_complete(self):
        """
        Operation to request all PTZ presets.

        Returns:
            Returns the complete presets Onvif.
        """
        request = self.__ptz.create_type('GetPresets')
        request.ProfileToken = self.__token
        ptz_get_presets = self.__ptz.GetPresets(request)
        return ptz_get_presets

    def remove_preset(self, preset_name: str):
        """
        Operation to remove a PTZ preset.

        Args:
            preset_name: Preset name.

        Returns:
            Return onvif's response.
        """
        presets = ONVIFCamera.get_preset_complete(self)
        request = self.__ptz.create_type('RemovePreset')
        request.ProfileToken = self.__token
        for i, _ in enumerate(presets):
            if str(presets[i].Name) == preset_name:
                request.PresetToken = presets[i].token
                ptz_remove_preset = self.__ptz.RemovePreset(request)
                return ptz_remove_preset
        return None

    def go_to_preset(self, preset_position: str):
        """
        Operation to go to a saved preset position.

        Args:
            preset_position: preset name.

        Returns:
            Return onvif's response.
        """
        presets = ONVIFCamera.get_preset_complete(self)
        request = self.__ptz.create_type('GotoPreset')
        request.ProfileToken = self.__token
        for i, _ in enumerate(presets):
            str1 = str(presets[i].Name)
            if str1 == preset_position:
                request.PresetToken = presets[i].token
                response = self.__ptz.GotoPreset(request)
                return response
        return None
