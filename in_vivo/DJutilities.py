# This code is to make decoding rhd/rhs/rhx format at once

# As I mentioned in "READ ME" file, code for reading data can be downloaded from the web site
# So you should have the file/code already which contains the function "load_file"
# after you correct save_path and read_path, type files_decoding(save_path,read_path)

import os 
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, lfilter
import matplotlib.pyplot as plt

# butter_bandpass requires cutting freuqency(low, high), samplingrate(fs), cutting magnitude?(order)
# it returns numerator(b) and denominator(a) of polynomials of the IIR filter
def butter_bandpass(lowcut, highcut, fs, order):
    # nyquist frequency. Nyquist theory explains that half of max frequency restores the original signal
    nyq = 0.5 * fs        
    low = lowcut / nyq
    high = highcut / nyq
    b,a = butter(order, [low, high], btype='band', analog = False)
    return b,a

# filtering process. filtfilt applies a digital filter forward and backward to a signal.
# it requires same as before and returns the filtered data
def butter_bandpass_filter(data, lowcut, highcut, fs, order ):
    b,a = butter_bandpass(lowcut, highcut, fs, order = order)
    y= filtfilt(b,a,data)  
    return y


# fast foureir transform. it returns frequency and magnitude
# however, the index of magnitude should be studied more...
def frequency_analysis(data, fs):
    data_length = len(data)
    fft = np.fft.fft(data) / data_length
    fft_magnitude = abs(fft)
    f = np.linspace(-(fs/2),(fs/2), len(data))
    z = np.fft.fftshift(fft_magnitude)
    
    # analysis_start= int(len(f)/2)
    # analysis_end = analysis_start + fs*2 # abtou 60
    
    return f, z 

# peak selection. but code below revision
# inclination_threshold is the threshold for ognoring noise
def find_peaks_arg(time, data, inclination_threshold, datarate, mode,
                   plot_individual_spike = False,
                   plot_spike_time = False,
                   plot_former_and_after = False,
                   plot_coincidence = False):
    
    # Firstly, showing abrupt gradient(difference) change will be selected
    # sicne differencing results in smaller datasize, appending is needed
    data_gradient = np.diff(data)
    data_gradient = np.append(data_gradient, data_gradient[-1])
    
    # drastic change indicates the points where the value is regarded as "USEFUL"
    
    # Here, need revision ( setting the proper points... )
    if mode == 'spike': 
        # Since the recording is done extracelluarly, neural activation will be represented as "SINK"
        drastic_change = ( data_gradient < -inclination_threshold ) & (data <  -np.median(abs(data)))       
        
        # interval literally means the time between each "SPIKE". 
        # Since we believe spike occurs maximum 5kHz, which is 1/0.0002 (spike/second)
        interval = int(datarate/ 5000 )
        
    elif mode =='lfp':
        # LFP, amplitude of data seem more valuable. 
        drastic_change = (abs(data) > inclination_threshold)
        
        # for lfp, given frequency is about ~500Hz -> /5 = 200ms(=5Hz), /50 = 20ms /500=2ms?    
        interval = int(datarate/500 )       
        
    drastic_change = np.where(drastic_change == True )[0]
    
    # this will show the number of saitsfying argument. 
    tim = []
    start = drastic_change[0]
    tmp_list = []  
    
    # this is the flow: get every section where the values are included?
    # we will get the maximum value of each section using (i+1) as index
    for i in range(0, len(drastic_change)-1): 
        
        # start will be changed below. It represents when the drastic change firstly occur
        # inter-spike interval is: change[i+1]-start  -> has to be more than (spike width * 2)
        # spike width is: change[i] - start
        # but need revision
        if (drastic_change[i+1] - start <= interval * 2) and (drastic_change[i] - start <= interval) :  
            tmp_list.append(i)
            pass
        else:
            # It will make error if there is abrupt spike( it results in  only one argument )
            # (tmp_list)==0 means that drastic_change[i] is not involved in the section
            if len(tmp_list) == 0 :     
                start = drastic_change[i+1]
                tmp_list = []
            else :
                # argmax indicates the number...
                tim.append(abs(data[start:drastic_change[i]]).argmax() + start+1) 
                start = drastic_change[i+1]
                tmp_list = []

    tim = list(set(tim))
    tim.sort()
    tim = np.array(tim)      

#     if mode == 'spike':
    positive_value = tim[data[tim] >0]
    negative_value = tim[data[tim] <0]

    tim = negative_value    # for clarity
    # array_tmp = np.arange(0,len(data),1)

    if plot_individual_spike == True:
        L_side = 2* interval
        R_side =  3* interval
        for i in tim:
            if i - L_side <0 or i + R_side > len(data):
                pass
            else:
                tmp_target = data[i-L_side:i+R_side]
                plt.plot(time[:L_side+R_side], tmp_target, alpha=0.5, label="time is "+str(time1[i])[:5])
                plt.legend(loc='upper right')
                plt.show()

    if plot_spike_time == True:
        plt.figure(figsize=(20,8))
        for i in tim:
            plt.axvline(time[i], ymin = 0.4, ymax=0.6, linewidth = 0.5, color='black')

    if plot_former_and_after == True:
        for i in drastic_change:
            plt.scatter(time[i], data[i], alpha=0.1, color = 'black')
        for i in tim:
            plt.scatter(time[i], data[i], color='red')

    if plot_coincidence == True:
        plt.plot(time,data, alpha=0.5)
        for i in tim:
            plt.scatter(time[i], data[i], color = 'black')
    return tim


def files_decoding(save_path,read_path,channel1, channel2):

    os.chdir(save_path)
    # os.walk returns all files in the separate folder
    # Folders are distinguished by the list []
    # if there is no folder in the path -> it will return only one list!
    for (roots, dirs, files) in os.walk(read_path):
        if len(files) > 0:   
            # Every file in the same folder is from the one creature, so data will be integrated
            # this process will be done by "df3.to_csv(... mode = 'a' )"
            # Integrated data will be named as before except for the format (files[0][:-4])
            name = files[0][:-4]+".csv"
            
            # if, the file was not decoded before, then it will start decoding process
            if name not in os.listdir(save_path):
                
                # Since the files contain the list of the file in the folder, this will separate each file
                for file_name in files:
                    
                    # is it rhs file?
                    if file_name.endswith(".rhs"):
                        try:
                            # show the file name
                            print(file_name)
                            
                            # file_tmp indicates the location of the file
                            file_tmp = os.path.join(roots,file_name)
                            result, data_present = load_file(file_tmp)
                            
                            # data frame...
                            if data_present:
                                df3 = pd.DataFrame()
                                df3[file_name+f"_{channel1}"] = result['amplifier_data'][channel1]
                                df3[file_name+f"_{channel2}"] = result['amplifier_data'][channel2]
                                df3.to_csv(save_path+"\\"+name, mode="a", header= False)
                        
                        # if file size is about 0, it will make errors.
                        except Exception:
                            continue


def save_figure(file, detection_mode, fs, order):
    print(file)
    
    df = pd.read_csv(file, header=None)
    df = df.drop(0, axis=1)

    df['first_filtered'] = butter_bandpass_filter(df[1],detection_mode[0],detection_mode[1],fs, order)
    df['second_filtered'] = butter_bandpass_filter(df[2],detection_mode[0],detection_mode[1],fs, order)

    freq_range, freq_amp = frequency_analysis(df['first_filtered'], 30000)
    freq_range2, freq_amp2 = frequency_analysis(df['second_filtered'], 30000)

    x_axis =  np.arange(0, len(df[1]))/30000

    fig = plt.figure(figsize=(16,8))
    ax1 = fig.add_subplot(4,1,1)
    ax2 = fig.add_subplot(4,1,2)
    ax3 = fig.add_subplot(4,1,3)
    ax4 = fig.add_subplot(4,1,4)

    ax1.plot(x_axis, df[1], label="raw_data_9")
    ax1.plot(x_axis, df["first_filtered"], label="filtered")
    ax1.set_ylim([-500,500])
    ax1.set_ylabel("Voltage (micro volts)")
    ax1.legend(loc = "upper right")

    ax2.plot(x_axis, df[2], label='raw_data_13')
    ax2.plot(x_axis, df["second_filtered"], label="filtered")
    ax2.set_ylim([-500,500])
    ax2.set_ylabel("Voltage (micro volts)")
    ax2.set_xlabel("time(second)")
    ax2.legend(loc = "upper right")


    ax3.plot(freq_range, freq_amp)
    ax3.set_ylabel("PSD? or?")
    ax3.set_xlim([0,100])


    ax4.plot(freq_range2, freq_amp2)
    ax4.set_ylabel("psd? or ?")
    ax4.set_xlabel("frequency(HZ)")
    ax4.set_xlim([0,100])
    fig.savefig(file[:-4]+'.jpeg', dpi=300)
    
    plt.clf()
    plt.close('all')