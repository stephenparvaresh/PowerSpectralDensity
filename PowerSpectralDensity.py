import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt  
from tqdm import notebook as tqdm
from tqdm import tqdm
import math
from scipy import signal,misc,stats

class PSDMaker():
    def __init__(self, data, participant_column, framerate, column, eye_metric):
        self.data = data
        self.participant_column = participant_column
        self.framerate = framerate
        self.column = column
        self.eye_metric = eye_metric
        
    def psd_maker(self):
        """
        Adds a power and corresponding frequency column to data. Subsets based on question and calculates psd from that

        Attributes:
            data: dataframe with unet mask output columns
            participant_column: column that calls individual participants
            framerate: framerate of videos
            column: column to divide up data by. Examples include type, demographic columns, PLR color, etc. 
            eye_metric: eye metric you want the PSD for. 

        Returns:
        psd_dataframe: the same df but with a power, frequency, and log(power) column. Added columns do not match length of original dataframe. 

        """
        
        if 'level_0' in self.data.columns:
            self.data = self.data.drop(['level_0'], axis = 1)


        # Establish the output df
        df = [0,0,0,0,0]

        # Reindex dataframe. Makes things easier later. 
        good_plr_1 = pd.DataFrame()
        for user in tqdm(self.data[self.participant_column].unique()):
            df_1 = self.data[self.data[self.participant_column] == user]
            df_1 = df_1.reset_index()
            good_plr_1 = good_plr_1.append(df_1)
        good_plr_1 = pd.DataFrame(good_plr_1)

        # The actual loop. Meant to run on one person at a time
        for user in tqdm(good_plr_1[self.participant_column].unique()):
            df_1 = good_plr_1[good_plr_1[self.participant_column] == user]
            for question in df_1[self.column].unique():

                # Subset data to just one question at a time per person
                q_data = df_1[df_1[self.column] == question]

                # Window size should always be bigger than the length of the data, and ideally a power of 2. This sets that
                nfft = 2**math.ceil(math.log2(len(q_data)))
        #             print(nfft, question)

                # Do the actual psd.
                power, freq = plt.psd(q_data[self.eye_metric], Fs=self.framerate, NFFT=nfft, window = signal.get_window('hamming', Nx = nfft, fftbins=True), detrend = 'mean', pad_to = nfft, noverlap = nfft/2)
                plt.close()

                log_power = np.log(power)
                # Build the new row for the output df
                psd_row = [question, power, freq, log_power, user]
                psd_row = np.array(psd_row)
                df = np.vstack([df, psd_row])

        df = pd.DataFrame(df, columns = [f'{self.column}', 'power_array', 'freq_array', 'log_power', f'{self.participant_column}'])

        # Remerge w/ original data
        # power and frequency repeat each row w/i a question so if there's a more optimal way to store data do that
        output_df = pd.merge(self.data, df, how = 'left', left_on=[self.data[self.column], self.participant_column], right_on=[df[self.column], self.participant_column])
        output_df_1 = pd.DataFrame()
        for user in tqdm(output_df[self.participant_column].unique()):
            df_1 = output_df[output_df[self.participant_column] == user]
            df_1 = df_1.reset_index()
            output_df_1 = output_df_1.append(df_1)
        output_df_1 = pd.DataFrame(output_df_1)
        output_df = output_df_1

        #Pull power and frequency arrays and make a dataframe
        power_psd = pd.DataFrame()
        for user in tqdm(output_df[self.participant_column].unique()):
            df_2 = output_df[output_df[self.participant_column] == user]
            power_array = df_2.power_array.iloc[0]
            freq_array = df_2.freq_array.iloc[0]
            power = pd.DataFrame(power_array, columns = ['power'])
            freq = pd.DataFrame(freq_array, columns = ['freq'])
            power_something_1 = pd.merge(power, freq, on=power.index)
            power_something_1[self.participant_column] = user
            power_psd=power_psd.append(power_something_1)

        power_psd = power_psd.drop(['key_0'], axis=1)
#         power_psd['power_log'] = np.log(power_psd['power'])
        output_df = output_df.drop(['key_0'], axis = 1)

        #Merge the two dataframes
        psd_dataframe = pd.merge(output_df, power_psd, how = 'left', left_on=[output_df.index, self.participant_column], right_on=[power_psd.index, self.participant_column], copy=False)

        #Clean up dataframes, remove columns, rename columns
        if 'level_0' in psd_dataframe.columns:
            psd_dataframe = psd_dataframe.drop(['level_0'], axis = 1)
        if 'key_0' in psd_dataframe.columns:
            psd_dataframe = psd_dataframe.drop(['key_0'], axis = 1)
        if 'index' in psd_dataframe.columns:
            psd_dataframe = psd_dataframe.drop(['index'], axis = 1)
        if f'{self.column}_y' in psd_dataframe.columns:
            psd_dataframe = psd_dataframe.drop([f'{self.column}_y'], axis = 1)
        if f'{self.column}_x' in psd_dataframe.columns:
            psd_dataframe = psd_dataframe.rename(columns = {f'{self.column}_x':f'{self.column}'})
        if 'freq_x' in psd_dataframe.columns:
            psd_dataframe = psd_dataframe.rename(columns = {'freq_x':'freq_array'})
        if 'power_x' in psd_dataframe.columns:
            psd_dataframe = psd_dataframe.rename(columns = {'power_x':'power_array'})
        if 'freq_y' in psd_dataframe.columns:
            psd_dataframe = psd_dataframe.rename(columns = {'freq_y':'freq'})
        if 'power_y' in psd_dataframe.columns:
            psd_dataframe = psd_dataframe.rename(columns = {'power_y':'power'})
        if 'log_power' in psd_dataframe.columns:
            psd_dataframe = psd_dataframe.rename(columns = {'log_power':'log_power_array'})

        return psd_dataframe
    
    def run(self):
        psd_maked = self.psd_maker()
        return psd_maked
