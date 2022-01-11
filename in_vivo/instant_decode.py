# This code is to make decoding rhd/rhs/rhx format at once

# As I mentioned in "READ ME" file, code for reading data can be downloaded from the web site
# So you should have the file/code already which contains the function "load_file"
# after you correct save_path and read_path, type files_decoding(save_path,read_path)

import os
import pandas as pd

# %run importrhsutilities.py
# %matplotlib inline

save_path = "D:/inu_invivo"
read_path = "E:/in vivo/recording"
channel1 = 9
channel2 = 13

def files_decoding(save_path,read_path):

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

files_decoding(save_path, read_path)