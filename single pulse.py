import os
import pyabf
import pyabf.filter
import matplotlib.pyplot as plt
import numpy as np
import xlsxwriter

abf = pyabf.ABF("C:/Users/DJ/Documents/Python Scripts/EPG/test.abf")         #files

result = []
count = 0
tim = []
temp_num = 0

abf.setSweep(7)

#  differencing, and multiply for easy calculation, then add '0' for the plot
result = np.diff(abf.sweepY)
result = np.append(result, [0])

# find 
#Is = np.where( result > result.std())[0]
Is = np.where( result > 0.2)[0]
fig = plt.figure()
highest_peak = 0
temporary = []

# find the steepest 

ls2 = []

for i in range(0, len(Is)):
    if result[Is[i]] >= result[Is[i]-1] and result[Is[i]] >= result[Is[i]+1]:    # fastest inclination; result[Is[i]]
        ls2.append(Is[i])
print(ls2)

for i in range(0, len(ls2)):
    if i == len(ls2)-1:
        print(i)
        tim.append(ls2[i])
        count += 1
        temporary = []
    else:
        
        if ls2[i+1] - ls2[i] <= 50 :
            temporary.append(ls2[i])
            
        else:
            if len(temporary) <= 1:
                tim.append(ls2[i])
                count += 1
                temporary = []
            
            else:       
                tim.append( int(np.mean(temporary)))
                count += 1 
                temporary =[]
        
        
    
    
'''
    if Is[i+1] - Is[i] <= 20 :
        if result[Is[i]] >= result[Is[i]-1] and result[Is[i]] >= result[Is[i]+1]:    # fastest inclination; result[Is[i]]
            temporary.append(Is[i])
        else:
            if temporary == []:
                tim.append(Is[i])
                count += 1
            
            else:                    
                tim.append(np.argmax(abf.sweepY[temporary]))
                count += 1 
                temporary =[]
    '''            


print(tim)
print(count)

#upper(211) image
ax1 = fig.add_subplot(311)
ax1.plot(abf.sweepX, abf.sweepY, color='r')               # Digital output number(0)
ax1.scatter(abf.sweepX[tim], abf.sweepY[tim], color='b')

ax2 = fig.add_subplot(312, sharex = ax1)
ax2.plot(abf.sweepX, result)

#down(212) image
ax3 = fig.add_subplot(313, sharex=ax1)
ax3.scatter(abf.sweepX[tim],result[tim])
print(count)
plt.show()

'''
            if max(abf.sweepY[Is[i]:Is[i]+20]) != abf.sweepY[Is[i]+19]:             # highest peak. to distinguish repeated interval 
                if i == 0:
                    temp_num = max(abf.sweepY[Is[i]:Is[i]+20])                      # temp
                    count += 1
                    tim.append(Is[i])
                else: 
                    
                    if temp_num == max(abf.sweepY[Is[i]:Is[i]+20]):
                        print(Is[i])
                        pass
                    else:
                        temp_num = max(abf.sweepY[Is[i]:Is[i]+20])
                        count += 1
                        tim.append(Is[i])'''
                        
                        


'''



for i in range(1,len(result)-1):
    if result[i] > 5000 and result[i-1] < result[i] and result[i]>result[i+1]:
        count += 1
        tim.append(i)

print(count)
print(tim)
for i in tim:
    print(result[i+8])
'''

'''
print(len(abf.sweepX), len(abf.sweepY))
print(type(abf.sweepX))
print(abf.sweepX[1])
'''

'''print(abf.headerText)
abf.headerLaunch()
print(abf.sweepY)
'''





































'''
# figure size
fig = plt.figure(figsize=(10, 8))               #figsize 

#upper(211) image
ax1 = fig.add_subplot(211)
ax1.grid(alpha=.2)
ax1.set_title("Digital Output 0")
ax1.set_ylabel("Digital Output")
#down(212) image
ax2 = fig.add_subplot(212, sharex=ax1)
ax2.grid(alpha=.2)
ax2.set_title("Recorded Waveform")
ax2.set_xlabel(abf.sweepLabelX)
ax2.set_ylabel("fEPSP(mV)")


# plot the digital output of the first sweep
ax1.plot(abf.sweepX, abf.sweepD(0), color='r')               # Digital output number(0)
ax1.set_yticks([0, 1])
ax1.set_yticklabels(["OFF", "ON"])
ax1.axes.set_ylim(-.5, 1.5)



# find out where Digital Output starts(ststart) and ends(stend)
abf2 = abf.sweepD(0)
dur = sum(np.where(abf2 == 1, True, False)) + 4*abf.dataPointsPerMs    # 4ms * data points per ms 
ststart= np.argmax(abf2 == 1)
stend = np.argmax(abf2 == 1) + dur - 1

# filter 
pyabf.filter.gaussian(abf,0)   # remove old filter
pyabf.filter.gaussian(abf,.2)   # apply filter(abf, sigma value)
voltages = []


# plot the data from every sweep
for sweepNumber in abf.sweepList:
    abf.setSweep(sweepNumber, baseline=[0.001,ststart/(1000*abf.dataPointsPerMs)])  # baseline, starts from ~ WTF
    ax2.plot(abf.sweepX, abf.sweepY, alpha=.5, lw=1)
    voltages.append(min(abf.sweepY[stend:]))    # Think about why sweepY starts from stend

# files save
os.chdir("C:\\Users\\DJ\\Documents\\Python Scripts\\EPG")          # directiory. must use \\

workbook = xlsxwriter.Workbook('C1.xlsx')                        # file name
worksheet = workbook.add_worksheet("tst2")
worksheet.write('A1','Trace')
worksheet.write('B1','Peak Amplitude')
num = 2   #where to start (1)
for i in voltages:
    worksheet.write('A{0}'.format(num),num-1)   #where to start (2)
    worksheet.write('B{0}'.format(num),i)
    num = num + 1
workbook.close()

# zoom in on an interesting region
ax2.axes.set_xlim(0.12,0.15)
ax2.axes.set_ylim()

'''