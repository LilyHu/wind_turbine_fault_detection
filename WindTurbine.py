import numpy as np
import datetime as dt
import pandas as pd

class EnerconWindTurbineData(object):


    """
	Initialises the class instance.

    Imports the data and returns arrays of SCADA & status data by
    calling import_data().

    Parameters
    ----------
    scada_data_file: str, optional
        The raw SCADA data csv file.
    status_data_wec_file: str, optional
        The status/fault csv file for the WEC
    status_data_rtu_file: str, optional
        The status/fault csv file for the RTU
    warning_data_wec_file: str, optional
        The warning/information csv file for the WEC
    warning_data_rtu_file: str, optional
        The warning/information csv file for the RTU
        
    Notes
    -----
    Both status_data_wec.csv & status_data_rtu.csv originally come from
    pes_extrainfo.csv, filtered according to their plant number.
    SCADA_data.csv contains the wsd, 03d and 04d data files all
    combined together.
    """

    def __init__(
            self, 
            scada_data_file='../Data/Source Data/SCADA_data.csv',
            status_data_wec_file='../Data/Source Data/status_data_wec.csv',
            status_data_rtu_file='../Data/Source Data/status_data_rtu.csv',
            warning_data_wec_file='../Data/Source Data/warning_data_wec.csv',
            warning_data_rtu_file='../Data/Source Data/warning_data_rtu.csv'):

        self.scada_data_file = scada_data_file
        self.status_data_wec_file = status_data_wec_file
        self.status_data_rtu_file = status_data_rtu_file
        self.warning_data_wec_file = warning_data_wec_file
        self.warning_data_rtu_file = warning_data_rtu_file
        
        # Pandas dataframe of the above
        self.status_data_wec = []
        
        # Pandas dataframe of all the scada data
        self.scada_data = []
        # Pandas dataframe of all the new features
        self.new_features = []
        # Pandas Series of labels
        self.ylabels = []

	"""
	This imports the data, and returns arrays of SCADA, status &
	warning data. Dates are converted to unix time, and strings are
	encoded in the correct format (unicode). Two new fields,
	"Inverter_averages" and "Inverter_std_dev", are also added to
	the SCADA data. These are the average and standard deviation of
	all Inverter Temperature fields.
	
	WARNING: The data is not every 10 minutes. There are errors, 
	large gaps in data, some values in between 10 minutes, and double values
	for the same time

	Set's the following fields
	-------
	self.scada_data: ndarray
		The imported and correctly formatted SCADA data
	self.status_data_wec: ndarray
		The imported and correctly formatted WEC status data
	self.status_data_rtu: ndarray
		The imported and correctly formatted RTU status data
	self.warning_data_wec: ndarray
		The imported and correctly formatted WEC warning data
	self.warning_data_rtu: ndarray
		The imported and correctly formatted RTU warning data
	"""
    def import_data(self):
        
        self.scada_data = np.genfromtxt(
            open(self.scada_data_file, 'rb'), dtype=(
                '<U19', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4',
                '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4',
                '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4',
                '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4',
                '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4',
                '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4',
                '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4', '<f4'),
            delimiter=",", names=True)
        
        self.status_data_wec = np.genfromtxt(
            open(self.status_data_wec_file, 'rb'), dtype=(
                '<U19', '<i4', '<i4', '<U9', '<U63', '<i4', '|b1', '|b1',
                '<f4'), delimiter=",", names=True)

        self.status_data_rtu = np.genfromtxt(
            open(self.status_data_rtu_file, 'rb'), dtype=(
                '<U19', '<i4', '<i4', '<U9', '<U63', '<i4', '|b1', '|b1',
                '<f4'), delimiter=",", names=True)

        self.warning_data_wec = np.genfromtxt(
            open(self.warning_data_wec_file, 'rb'), dtype=(
                '<U19', '<i4', '<i4', '<U9', '<U63', '|b1', '<f4'),
            delimiter=",", names=True)

        self.warning_data_rtu = np.genfromtxt(
            open(self.warning_data_rtu_file, 'rb'), dtype=(
                '<U19', '<i4', '<i4', '<U9', '<U63', '|b1', '<f4'),
            delimiter=",", names=True)

        self.scada_data = pd.DataFrame(self.scada_data)

        # Add 2 extra columns to scada - Inverter_averages and
        # Inverter_std_dev, as features
        inverters = np.array([
            'CS101__Sys_1_inverter_1_cabinet_temp',
            'CS101__Sys_1_inverter_2_cabinet_temp',
            'CS101__Sys_1_inverter_3_cabinet_temp',
            'CS101__Sys_1_inverter_4_cabinet_temp',
            'CS101__Sys_1_inverter_5_cabinet_temp',
            'CS101__Sys_1_inverter_6_cabinet_temp',
            'CS101__Sys_1_inverter_7_cabinet_temp',
            'CS101__Sys_2_inverter_1_cabinet_temp',
            'CS101__Sys_2_inverter_2_cabinet_temp',
            'CS101__Sys_2_inverter_3_cabinet_temp',
            'CS101__Sys_2_inverter_4_cabinet_temp'])
        means = pd.Series(self.scada_data[inverters].mean(axis=1), name='Inverter_averages')
        stds = pd.Series(self.scada_data[inverters].std(axis=1), name='Inverter_std_dev')
    
		# Save the scada data and the inverter means and standard deviations as "scada_data"
        self.scada_data = pd.concat([self.scada_data, means, stds], axis=1)
		
        # Convert the unix time in the "Time" column to pandas datetime and set the 'Time' column to be the index
        self.scada_data["Time"] = pd.to_datetime(self.scada_data["Time"], format='%d/%m/%Y %H:%M:%S')- pd.Timedelta('1h')
        self.scada_data = self.scada_data.set_index("Time", drop=True)
        
		# Sort the data by timestamp
        self.scada_data.sort_index(inplace=True)
        
		# Convert the unix time in the "Time" column to pandas datetime and set the 'Time' column to be the index
        self.status_data_wec = pd.DataFrame(self.status_data_wec)
        self.status_data_wec["Time"] = pd.to_datetime(self.status_data_wec["Time"], format='%d/%m/%Y %H:%M:%S')- pd.Timedelta('1h')
        self.status_data_rtu = pd.DataFrame(self.status_data_rtu)
        self.status_data_rtu["Time"] = pd.to_datetime(self.status_data_rtu["Time"], format='%d/%m/%Y %H:%M:%S')- pd.Timedelta('1h')
        self.warning_data_wec = pd.DataFrame(self.warning_data_wec)
        self.warning_data_wec["Time"] = pd.to_datetime(self.warning_data_wec["Time"], format='%d/%m/%Y %H:%M:%S')- pd.Timedelta('1h')
        self.warning_data_rtu = pd.DataFrame(self.warning_data_rtu)
        self.warning_data_rtu["Time"] = pd.to_datetime(self.warning_data_rtu["Time"], format='%d/%m/%Y %H:%M:%S')- pd.Timedelta('1h')

	'''
	Optionally inport the data from pickle files
	'''
    def import_from_pickle_files(self):
        self.scada_data = pd.read_pickle('scada_data')
        # Reload the expert features, mean features, and std features
        self.new_features = pd.read_pickle('expert_')
        self.mean_std = pd.read_pickle('mean_std')
        pd.DataFrame.dropna(self.mean_std, inplace=True)
        #edata.new_features = pd.concat([edata.new_features, edata.mean_std], axis=1)
        self.create_lagged_features(6)
        # edata.derived_features = pd.concat(axis=1, join='inner')
        self.derived_features = pd.concat([self.new_features, self.mean_std, self.lagged_features], axis=1, join='inner')
        self.status_data_wec = pd.read_pickle('status_data_wec')
        self.status_data_rtu = pd.read_pickle('status_data_rtu')
        self.warning_data_wec = pd.read_pickle('warning_data_wec')
        self.warning_data_rtu = pd.read_pickle('warning_data_rtu')
        
        self.create_labels()
    
	'''
	Removes data that is not on the 10 min dot
	Replaces repetitive timestamps with the mean
	Removes the known faulty data
	'''    
    def clean_data(self):
        
        # Keep only the 10 minute samples
        self.scada_data = self.scada_data[self.scada_data.index.minute % 10 == 0]
        
        # Check for identical timestamps and take the average
        self.scada_data.sort_index(inplace=True)
        start_of_dupes = 0
        for i in range(1, len(self.scada_data) + 1):
            if i == len(self.scada_data) or self.scada_data.index[i] != self.scada_data.index[i - 1]:
                if i - start_of_dupes > 1:
                    average = self.scada_data.iloc[start_of_dupes:i].mean()
                    self.scada_data.iloc[start_of_dupes] = average
                start_of_dupes = i
        self.scada_data["___INDEX___"] = self.scada_data.index
        self.scada_data.drop_duplicates(subset="___INDEX___", keep="first", inplace=True)
        self.scada_data.drop("___INDEX___", axis=1, inplace=True)
        
        # Remove the faulty blade temps
        self.scada_data.drop(['CS101__Blade_A_temp', 'CS101__Blade_B_temp', 'CS101__Blade_C_temp'], axis=1, inplace=True)
        
		# Remove the faulty inverters
        self.scada_data.drop([ 'CS101__Sys_2_inverter_5_cabinet_temp', 'CS101__Sys_2_inverter_6_cabinet_temp','CS101__Sys_2_inverter_7_cabinet_temp'], axis=1, inplace=True)
        self.scada_data.drop(['WEC_Operating_Hours', 'WEC_Production_kWh', 'WEC_Production_minutes'], axis=1, inplace=True)
        self.scada_data.drop(['Error'], axis=1, inplace=True)
     
	'''
	Create new engineering features from the scada_data
	'''
    def create_new_features(self):
        # Create new dataframe for new features
        self.new_features = pd.DataFrame(index=self.scada_data.index)

        # Calculate averages
        self.new_features['Avg_Sys_1_inverters_cabinet_temp']  = self.scada_data[['CS101__Sys_1_inverter_1_cabinet_temp',
               'CS101__Sys_1_inverter_2_cabinet_temp',
               'CS101__Sys_1_inverter_3_cabinet_temp',
               'CS101__Sys_1_inverter_4_cabinet_temp',
               'CS101__Sys_1_inverter_5_cabinet_temp',
               'CS101__Sys_1_inverter_6_cabinet_temp',
               'CS101__Sys_1_inverter_7_cabinet_temp']].mean(axis=1)

        self.new_features['Avg_Sys_2_inverters_cabinet_temp'] = self.scada_data[['CS101__Sys_2_inverter_1_cabinet_temp',
               'CS101__Sys_2_inverter_2_cabinet_temp',
               'CS101__Sys_2_inverter_3_cabinet_temp',
               'CS101__Sys_2_inverter_4_cabinet_temp']].mean(axis=1)

        self.new_features['Avg_bearing_temp'] = self.scada_data[['CS101__Front_bearing_temp', 'CS101__Rear_bearing_temp',]].mean(axis=1)

        self.new_features['Avg_pitch_cabinet_blade_temp'] = self.scada_data[['CS101__Pitch_cabinet_blade_A_temp',
               'CS101__Pitch_cabinet_blade_B_temp',
               'CS101__Pitch_cabinet_blade_C_temp',]].mean(axis=1)

        self.new_features['Avg_rotor_temp'] = self.scada_data[[ 'CS101__Rotor_temp_1',
               'CS101__Rotor_temp_2']].mean(axis=1)

        self.new_features['Avg_stator_temp'] = self.scada_data[['CS101__Stator_temp_1', 'CS101__Stator_temp_2',]].mean(axis=1)

        self.new_features['Avg_nacelle_ambient_temp'] = self.scada_data[['CS101__Nacelle_ambient_temp_1', 
                                                                           'CS101__Nacelle_ambient_temp_2']].mean(axis=1)
        
        # Create features based on differences

        # Max and Min of (wind speed, rotation, power, reactive power)
        self.new_features['Dif_max_min_windspeed'] = self.scada_data['WEC__max_windspeed'] - self.scada_data['WEC__min_windspeed']
        self.new_features['Dif_max_min_rotation'] = self.scada_data['WEC_max_Rotation'] - self.scada_data['WEC_min_Rotation']
        self.new_features['Dif_max_min_Power'] = self.scada_data['WEC_max_Power'] - self.scada_data['WEC_min_Power']
        self.new_features['Dif_max_min_reactive_Power'] = self.scada_data['WEC_max_reactive_Power'] - self.scada_data['WEC_min_reactive_Power']

        # Max and Average of (wind speed, rotation, power, reactive power)
        self.new_features['Dif_max_avg_windspeed'] = self.scada_data['WEC__max_windspeed'] - self.scada_data['WEC_ava_windspeed']
        self.new_features['Dif_max_avg_rotation'] = self.scada_data['WEC_max_Rotation'] - self.scada_data['WEC_ava_Rotation']
        self.new_features['Dif_max_avg_Power'] = self.scada_data['WEC_max_Power'] - self.scada_data['WEC_ava_Power']
        self.new_features['Dif_max_avg_reactive_Power'] = self.scada_data['WEC_max_reactive_Power'] - self.scada_data['WEC_ava_reactive_Power']

        # Min and Average of (wind speed, rotation, power, reactive power)\\
        self.new_features['Dif_avg_min_windspeed'] = self.scada_data['WEC_ava_windspeed'] - self.scada_data['WEC__min_windspeed']
        self.new_features['Dif_avg_min_rotation'] = self.scada_data['WEC_ava_Rotation'] - self.scada_data['WEC_min_Rotation']
        self.new_features['Dif_avg_min_Power'] = self.scada_data['WEC_ava_Power'] - self.scada_data['WEC_min_Power']
        self.new_features['Dif_avg_min_reactive_Power'] = self.scada_data['WEC_ava_reactive_Power'] - self.scada_data['WEC_min_reactive_Power']

        # Available Power (from wind, technical reasons, force majeure reasons, force external reasons)\\
        self.new_features['Diff_P_wind_P_technical'] = self.scada_data['WEC_ava_available_P_from_wind'] - self.scada_data['WEC_ava_available_P_technical_reasons']
        self.new_features['Diff_P_wind_P_majeure'] = self.scada_data['WEC_ava_available_P_from_wind'] - self.scada_data['WEC_ava_Available_P_force_majeure_reasons']
        self.new_features['Diff_P_wind_P_technical'] = self.scada_data['WEC_ava_available_P_from_wind'] - self.scada_data['WEC_ava_Available_P_force_external_reasons']
        self.new_features['Diff_P_technical_P_majeure'] = self.scada_data['WEC_ava_available_P_technical_reasons'] - self.scada_data['WEC_ava_Available_P_force_majeure_reasons']
        self.new_features['Diff_P_technical_P_external'] = self.scada_data['WEC_ava_available_P_technical_reasons'] - self.scada_data['WEC_ava_Available_P_force_external_reasons']
        self.new_features['Diff_P_majeure_P_external'] = self.scada_data['WEC_ava_Available_P_force_majeure_reasons'] - self.scada_data['WEC_ava_Available_P_force_external_reasons']

        # Average Power and Available power (from wind, technical reasons, force majeure reasons, force external reasons)\\
        self.new_features['Diff_avg_Power_P_wind'] = self.scada_data['WEC_ava_Power'] - self.scada_data['WEC_ava_available_P_from_wind']
        self.new_features['Diff_avg_Power_P_wind'] = self.scada_data['WEC_ava_Power'] - self.scada_data['WEC_ava_available_P_technical_reasons']
        self.new_features['Diff_avg_Power_P_wind'] = self.scada_data['WEC_ava_Power'] - self.scada_data['WEC_ava_Available_P_force_majeure_reasons']
        self.new_features['Diff_avg_Power_P_wind'] = self.scada_data['WEC_ava_Power'] - self.scada_data['WEC_ava_Available_P_force_external_reasons']

        # Inverter Cabinet Temperatures
        # Inverter Cabinet Temperatures and Average Inverter Cabinet Temperature by system
        self.new_features['Diff_Avg_Sys_1_inverter_1']  = self.scada_data['CS101__Sys_1_inverter_1_cabinet_temp'] - self.new_features['Avg_Sys_1_inverters_cabinet_temp']
        self.new_features['Diff_Avg_Sys_1_inverter_2']  = self.scada_data['CS101__Sys_1_inverter_2_cabinet_temp'] - self.new_features['Avg_Sys_1_inverters_cabinet_temp']
        self.new_features['Diff_Avg_Sys_1_inverter_3']  = self.scada_data['CS101__Sys_1_inverter_3_cabinet_temp'] - self.new_features['Avg_Sys_1_inverters_cabinet_temp']
        self.new_features['Diff_Avg_Sys_1_inverter_4']  = self.scada_data['CS101__Sys_1_inverter_4_cabinet_temp'] - self.new_features['Avg_Sys_1_inverters_cabinet_temp']
        self.new_features['Diff_Avg_Sys_1_inverter_5']  = self.scada_data['CS101__Sys_1_inverter_5_cabinet_temp'] - self.new_features['Avg_Sys_1_inverters_cabinet_temp']
        self.new_features['Diff_Avg_Sys_1_inverter_6']  = self.scada_data['CS101__Sys_1_inverter_6_cabinet_temp'] - self.new_features['Avg_Sys_1_inverters_cabinet_temp']
        self.new_features['Diff_Avg_Sys_1_inverter_7']  = self.scada_data['CS101__Sys_1_inverter_7_cabinet_temp'] - self.new_features['Avg_Sys_1_inverters_cabinet_temp']
        
        self.new_features['Diff_Avg_Sys_2_inverter_1']  = self.scada_data['CS101__Sys_2_inverter_1_cabinet_temp'] - self.new_features['Avg_Sys_2_inverters_cabinet_temp']
        self.new_features['Diff_Avg_Sys_2_inverter_2']  = self.scada_data['CS101__Sys_2_inverter_2_cabinet_temp'] - self.new_features['Avg_Sys_2_inverters_cabinet_temp']
        self.new_features['Diff_Avg_Sys_2_inverter_3']  = self.scada_data['CS101__Sys_2_inverter_3_cabinet_temp'] - self.new_features['Avg_Sys_2_inverters_cabinet_temp']
        self.new_features['Diff_Avg_Sys_2_inverter_4']  = self.scada_data['CS101__Sys_2_inverter_4_cabinet_temp'] - self.new_features['Avg_Sys_2_inverters_cabinet_temp']
                                                                          

        # Front and Rear Bearing Temperature
        self.new_features['Diff_font_rear_bearing'] = self.scada_data['CS101__Front_bearing_temp'] - self.scada_data['CS101__Rear_bearing_temp']

        # Average Bearing Temperature and (Front and Rear Bearing Temperature)
        self.new_features['Diff_font_avg_bearing'] = self.scada_data['CS101__Front_bearing_temp'] - self.new_features['Avg_bearing_temp']
        self.new_features['Diff_rear_avg_bearing'] = self.scada_data['CS101__Rear_bearing_temp'] - self.new_features['Avg_bearing_temp']

        # Pitch Cabinet Blade Temperatures
        self.new_features['Diff_cabinet_A_B_temp']= self.scada_data['CS101__Pitch_cabinet_blade_A_temp'] - self.scada_data['CS101__Pitch_cabinet_blade_B_temp']
        self.new_features['Diff_cabinet_A_C_temp']= self.scada_data['CS101__Pitch_cabinet_blade_A_temp'] - self.scada_data['CS101__Pitch_cabinet_blade_C_temp']
        self.new_features['Diff_cabinet_B_C_temp']= self.scada_data['CS101__Pitch_cabinet_blade_B_temp'] - self.scada_data['CS101__Pitch_cabinet_blade_C_temp']

        # Average Pitch Cabinet Blade Temperature and Pitch Cabinet Blade Temperatures
        self.new_features['Diff_cabinet_A_avg_temp'] = self.scada_data['CS101__Pitch_cabinet_blade_A_temp'] - self.new_features['Avg_pitch_cabinet_blade_temp']
        self.new_features['Diff_cabinet_B_avg_temp'] = self.scada_data['CS101__Pitch_cabinet_blade_B_temp'] - self.new_features['Avg_pitch_cabinet_blade_temp']
        self.new_features['Diff_cabinet_C_avg_temp'] = self.scada_data['CS101__Pitch_cabinet_blade_C_temp'] - self.new_features['Avg_pitch_cabinet_blade_temp']

        # Rotor Temperatures
        self.new_features['Diff_rotor_temps'] = self.scada_data['CS101__Rotor_temp_1'] - self.scada_data['CS101__Rotor_temp_2']

        # Average Rotor Temperature and Rotor Temperatures
        self.new_features['Dif_rotor_1_avg_temps'] = self.scada_data['CS101__Rotor_temp_1'] - self.new_features['Avg_rotor_temp']
        self.new_features['Dif_rotor_2_avg_temps'] = self.scada_data['CS101__Rotor_temp_2'] - self.new_features['Avg_rotor_temp']

        # Stator Temperatures
        self.new_features['Diff_stator_temps'] = self.scada_data['CS101__Stator_temp_1'] - self.scada_data['CS101__Stator_temp_2']

        # Average Stator Temperature and Stator Temperatures
        self.new_features['Diff_stator_1_avg_temps'] = self.scada_data['CS101__Stator_temp_1'] - self.new_features['Avg_stator_temp']
        self.new_features['Diff_stator_2_avg_temps'] = self.scada_data['CS101__Stator_temp_2'] - self.new_features['Avg_stator_temp']

        # Nacelle Ambient Temperatures
        self.new_features['Diff_nacelle_ambient_temps'] = self.scada_data['CS101__Nacelle_ambient_temp_1'] - self.scada_data['CS101__Nacelle_ambient_temp_2']

        # Average Nacelle Ambient Temperatures and Nacelle Temperatures
        self.new_features['Diff_avg_nacelle_ambient_temp'] = self.scada_data['CS101__Nacelle_ambient_temp_1'] - self.new_features['Avg_nacelle_ambient_temp']
        self.new_features['Diff_avg_nacelle_ambient_temp'] = self.scada_data['CS101__Nacelle_ambient_temp_2'] - self.new_features['Avg_nacelle_ambient_temp']

        #  Nacelle Temperature and Nacelle Cabinet Temperature
        self.new_features['Diff_nacelle_cabinet_temp'] = self.scada_data['CS101__Nacelle_temp'] - self.scada_data['CS101__Nacelle_cabinet_temp']

        # Ambient Temperature and (Nacelle Temperature, Nacelle Cabinet Temperatures, Main Carrier Temperature, Rectifier Temperature, Inverter Cabinet Temperature, Tower Temperature, Control Cabinet Temperature, Transformer Temperature)
        self.new_features['Diff_ambient_nacelle_temp'] = self.scada_data['CS101__Ambient_temp'] - self.scada_data['CS101__Nacelle_temp']
        self.new_features['Diff_ambient_nacelle_cabinet_temp'] = self.scada_data['CS101__Ambient_temp'] - self.scada_data['CS101__Nacelle_cabinet_temp']
        self.new_features['Diff_ambient_rectifier_temp'] = self.scada_data['CS101__Ambient_temp'] - self.scada_data['CS101__Rectifier_cabinet_temp']
        self.new_features['Diff_ambient_main_carrier_temp'] = self.scada_data['CS101__Ambient_temp'] - self.scada_data['CS101__Main_carrier_temp']
        self.new_features['Diff_ambient_yaw_inverter_cabinet_temp'] = self.scada_data['CS101__Ambient_temp'] - self.scada_data['CS101__Yaw_inverter_cabinet_temp']
        self.new_features['Diff_ambient_fan_inverter_cabinet_temp'] = self.scada_data['CS101__Ambient_temp'] - self.scada_data['CS101__Fan_inverter_cabinet_temp']
        self.new_features['Diff_ambient_tower_temp'] = self.scada_data['CS101__Ambient_temp'] - self.scada_data['CS101__Tower_temp']
        self.new_features['Diff_ambient_control_cabinet_temp'] = self.scada_data['CS101__Ambient_temp'] - self.scada_data['CS101__Control_cabinet_temp']
        self.new_features['Diff_ambient_transformer_temp'] = self.scada_data['CS101__Ambient_temp'] - self.scada_data['CS101__Transformer_temp']

        # Generator Temperature and Nacelle Temperature
        self.new_features['Diff_nacelle_stator_1_temp'] = self.scada_data['CS101__Nacelle_temp'] - self.scada_data['CS101__Stator_temp_1'] 
        self.new_features['Diff_nacelle_stator_2_temp'] = self.scada_data['CS101__Nacelle_temp'] - self.scada_data['CS101__Stator_temp_2'] 
        self.new_features['Diff_nacelle_rotor_1_temp'] = self.scada_data['CS101__Nacelle_temp'] - self.scada_data['CS101__Rotor_temp_1'] 
        self.new_features['Diff_nacelle_rotor_2_temp'] = self.scada_data['CS101__Nacelle_temp'] - self.scada_data['CS101__Rotor_temp_2'] 

    '''
	Create the mean and standard deviation features. 
	These calculations take a long time
	'''
    def create_mean_std_features(self):
        """
        Calculate the 2hr mean and standard deviation for self.scada_data
        Saves the new features in self.mean_std
        """
        # Make a temporary new dataframe
        self.mean_std = pd.DataFrame(index=self.scada_data.index)
        temp_features = self.scada_data.copy()
        temp_features[:] = np.nan
        for time in self.scada_data.index: # Calculate the 2 hr average for the column
            if len(self.scada_data.loc[time-pd.Timedelta('2hr'):time])== 13:
                temp_features.loc[time] = self.scada_data.loc[time-pd.Timedelta('2hr'):time].mean(axis=0)
        # Rename the new columns
        new_column_names = []
        for name in self.scada_data.columns.values:
            if len(self.scada_data.loc[time-pd.Timedelta('2hr'):time])== 13:
                new_column_names.append("2hr_mean_" + name) 
        temp_features.columns = new_column_names # Rename the columns
        # Join the temporary features with the new one
        self.mean_std = pd.concat([temp_features, self.mean_std], axis=1)

        # Make a temporary new dataframe
        temp_features = self.scada_data.copy()
        temp_features[:] = np.nan
        for time in self.scada_data.index: # Calculate the 2 hr average for the column
            temp_features.loc[time] = self.scada_data.loc[time-pd.Timedelta('2hr'):time].std()
        # Rename the new columns
        new_column_names = []
        for name in self.scada_data.columns.values:
            new_column_names.append("2hr_std_" + name) 
        temp_features.columns = new_column_names # Rename the columns
        # Join the temporary features with the new one
        self.mean_std = pd.concat([temp_features, self.mean_std], axis=1)

	'''
	Include lagged variables of self.scada_data
	New features are saved in self.lagged_features
	'''
    def create_lagged_features(self, n):
        
        self.lagged_features = pd.DataFrame(index=self.scada_data.index)
        
        for i in range(1, n+1):
            self.temp_lagged_features = self.scada_data.copy()

            # Introduce the delay or lagged features
            self.temp_lagged_features.index = self.temp_lagged_features.index +pd.Timedelta(str(i*10) + 'm')

            # Rename the new columns
            new_column_names = []
            for name in self.scada_data.columns.values:
                new_column_names.append(str(name) + '_t-' + str(i*10) + 'min') 
            self.temp_lagged_features.columns = new_column_names # Rename the columns
            
            self.lagged_features = pd.concat([self.lagged_features, self.temp_lagged_features], axis=1, join='inner')
    
	'''
	Creates a new pandas.Series with the same index as self.scada_data called self.ylabels
	self.ylabels = 0 except for the 5 main faults, whereby self.ylabels = Main Status
	
	Creates:
		self.ylabels
	'''    
    def create_labels(self):
        
        fault_main_statuses = (80, 62, 228, 60, 9)
        self.ylabels = pd.Series(index = self.derived_features.index)
        self.ylabels[:] = 0
        for i in range(0, len(self.status_data_wec)):
            current_status = self.status_data_wec.iloc[i]['Main_Status'] 
            if current_status in fault_main_statuses:
                start_time = self.status_data_wec.iloc[i]['Time']
                if i == (len(self.status_data_wec)-1):
                    self.ylabels[self.ylabels.index > start_time] = current_status
                else:
                    end_time = self.status_data_wec.iloc[i+1]['Time']
                    self.ylabels[(self.ylabels.index > start_time) & (self.ylabels.index < end_time)] = current_status
       
