import math
import matplotlib.pyplot as plt
import pandas as pd

class PSD():
    """ Power Spectral Density is useful for analyzing signals 
    in a variety of applications
    
    Attributes:
        data (dataFrame) represents original dataframe
        feature_1 (dataFrame column) represents feature to filter unique values
        feature_2 (dataFrame column) represents feature to filter unique values
        signal (dataFrame column) represents feature the PSD calculation will be run on
        
    """    
    def __init__(self, data, feature_1, feature_2, signal):
        self.data = data
        self.feature_1 = feature_1
        self.feature_2 = feature_2
        self.signal = signal
    
    def next_power_of_2(dataframe):
        """With the input of a number, this finds the next power of 2 greater than it. So 1000 returns 1024, 
        while 1025 would return 2048

        Args:
            int: length of data 

        Returns:
            int: next power of 2 greater than input
        """
        
        npt = 2**math.ceil(math.log2(dataframe))

        return npt


    def psd_maker(self):
        """
        Adds a power and corresponding rfrequency column to data. 

        Args:
            data (dataFrame): df with relevant eye data. Assumes data from only ONE feature_1
            feature_1 (dataFrame column): feature from dataframe to filter unique values
            feature_1 (dataFrame column): feature from dataframe to filter unique values
            signal (dataFrame column): signal the PSD calculation will be run on

        Returns:
        
           output_df (dataFrame): original dataFrame with power and frequency columns with the same values 
           within each unique feature_2

        """

        # Establish the output df
        df = pd.DataFrame(columns = [self.feature_2 ,'power', 'freq', 'log_power'])


        # The actual loop. Meant to run on one person at a time
        for x in self.data[self.feature_1].unique():
            df_1 = self.data[self.data[self.feature_1] == x]
            for y in df_1[self.feature_2].unique():
                # Subset data to just one feature_2 at a time per feature_1
                q_data = df_1[df_1[self.feature_2] == y]

                # Window size should always be bigger than the length of the data, and ideally a power of 2.
                nfft = next_power_of_2(len(q_data))

                # Do the actual psd.
                power, freq = plt.psd(q_data[self.signal], Fs=110, NFFT=nfft, window = signal.get_window('hamming', Nx = nfft, fftbins=True), detrend = 'mean', pad_to = nfft, noverlap = nfft/2)
                plt.close()

                log_power = np.log(power)
                # Build the new row for the output df
                psd_row = pd.DataFrame([[y, power, freq, log_power]], 
                                       columns = [self.feature_2, 'power', 'freq', 'log_power'])

                # Add the next row of data    
                df = pd.concat([df, psd_row])

        # Remerge w/ original data
        # power and frequency repeat each row w/i a question so if there's a more optimal way to store data do that
        output_df = self.data.merge(right=df, on=feature_2)
        self.data = output_df
        
        return self.data
    
    def power_plr(df):  
        """ The PSD returns new columns that contain objects. To do calcualtions on this data, the object
        must be split into inividual pieces.
        
        Args:
            None
        Returns:
            New dataFrame with power and frequency values in individual rows 
        """
        power_psd = pd.DataFrame()
        for x in tqdm(self.data[self.feature_1].unique()):
            df_1 = self.data[self.data[self.feature_1] == x]
            for y in df_1[feature_2].unique():
                df_2 = df_1[df_1[feature_2] == y]
                power_array = df_2.power.iloc[0]
                freq_array = df_2.freq.iloc[0]
                power = pd.DataFrame(power_array, columns = ['power'])
                freq = pd.DataFrame(freq_array, columns = ['freq'])
                x = df_2[feature_1].iloc[0]
                y = df_2[feature_2].iloc[0]
                df_3 = pd.merge(power, freq, on=power.index)
                power_plr_psd=power_plr_psd.append(df_3)
                
        return power_plr_psd
    
    def run(self):
        output_df = self.psd_maker()
        return output_df
        power_plr_psd = self.power_plr()
        return power_plr_psd