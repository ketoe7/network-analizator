import json
import os


class GeneralConfig:
    def __init__(self):
        self.config = f'{os.path.dirname(os.path.realpath(__file__))}/general_config.json'
        '''
        '''
        self.transmission_radius_range = 0
        '''
        '''
        self.time_sample = 0
        '''
        '''
        self.simulation_time = 0
        '''
        '''
        self.transmission_duration = 0
        '''
        '''
        self.idle_duration = 0
        '''
        '''
        self.blood_volume = 0

        if os.path.isfile(self.config):
            with open(self.config) as f:
                data = json.load(f)
                if 'transmission_radius_range' in data:
                    self.transmission_radius_range = data['transmission_radius_range']
                if 'time_sample' in data:
                    self.time_sample = data['time_sample']
                if 'simulation_time' in data:
                    self.simulation_time = data['simulation_time']
                if 'transmission_duration' in data:
                    self.transmission_duration = data['transmission_duration']
                if 'idle_duration' in data:
                    self.idle_duration = data['idle_duration']
                if 'blood_volume' in data:
                    self.blood_volume = data['blood_volume']