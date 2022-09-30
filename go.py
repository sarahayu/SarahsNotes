# brew install portaudio
# pip install pyaudio

import pyaudio
import wave
import audioop
import math
import numpy
from collections import deque


N = 410		        	# block size
# samples[96]	# buffer to store N samples
# count	    	# samples count
# flag	    	# flag set when the samples buffer is full with N samples
# new_dig		# flag set when inter-digit interval (pause) is detected

power_all = [0, 0, 0, 0, 0, 0, 0, 0]		# array to store calculated power of 8 frequencies

coeff = [ 31548, 31281, 30950, 30556, 29143, 28360, 27408, 26258 ]			# array to store the calculated coefficients                                                                   
f_tone = [ 697, 770, 852, 941, 1209, 1336, 1477, 1633 ]	# frequencies of rows & columns 

def goertzel (sample, coeff, N):
#initialize variables to be used in the function
#   Q, Q_prev, Q_prev2, i
#   prod1, prod2, prod3, power

  Q_prev = 0			#set delay element1 Q_prev as zero
  Q_prev2 = 0			#set delay element2 Q_prev2 as zero
  power = 0			#set power as zero

#   coeff = (2 * math.cos(2 * 3.14159265 * (freq / 16000)))
  for i in range(0, N):	# loop N times and calculate Q, Q_prev, Q_prev2 at each iteration
      Q = (sample[i]) + ((coeff * Q_prev) >> 14) - (Q_prev2)	# >>14 used as the coeff was used in Q15 format
      Q_prev2 = Q_prev		# shuffle delay elements
      Q_prev = Q

  #calculate the three products used to calculate power
  prod1 = Q_prev * Q_prev
  prod2 = Q_prev2 * Q_prev2
  prod3 = Q_prev * coeff >> 14
  prod3 = (prod3 * Q_prev2)

  power = ((prod1 + prod2 - prod3)) >> 8	#calculate power using the three products and scale the result down

  return round(power)

new_dig = 0

confidences = {
    '0': [ 100, 100 ],
    '1': [ 100, 100 ],
    '2': [ 100, 100 ],
    '3': [ 100, 100 ],
    '4': [ 100, 100 ],
    '5': [ 100, 100 ],
    '6': [ 100, 100 ],
    '7': [ 100, 100 ],
    '8': [ 100, 100 ],
    '9': [ 100, 100 ],
    'A': [ 100, 100 ],
    'B': [ 100, 100 ],
    'C': [ 100, 100 ],
    'D': [ 100, 100 ],
    '*': [ 100, 100 ],
    '#': [ 100, 100 ],
}

min_powers = {
    '0': [ 1000, 1000 ],
    '1': [ 1000, 1000 ],
    '2': [ 1000, 1000 ],
    '3': [ 1000, 1000 ],
    '4': [ 1000, 1000 ],
    '5': [ 1000, 1000 ],
    '6': [ 1000, 1000 ],
    '7': [ 1000, 1000 ],
    '8': [ 1000, 1000 ],
    '9': [ 1000, 1000 ],
    'A': [ 1000, 1000 ],
    'B': [ 1000, 1000 ],
    'C': [ 1000, 1000 ],
    'D': [ 1000, 1000 ],
    '*': [ 1000, 1000 ],
    '#': [ 1000, 1000 ],
}

def post_test():
    global new_dig, power_all
#---------------------------------------------------------------#     

#initialize variables to be used in the function
#   int i, row, col, max_power
    row = 0
    col = 0

    row_col = [
        ['1', '2', '3', 'A'],
        ['4', '5', '6', 'B'],
        ['7', '8', '9', 'C'],
        ['*', '0', '#', 'D'],
    ]
  

# find the maximum power in the row frequencies and the row number
    prev_max_power = 0
    max_power = 0		        #initialize max_power=0

    for i in range(0, 4):	    #loop 4 times from 0>3 (the indecies of the rows)

        if (power_all[i] > max_power):	#if power of the current row frequency > max_power
            prev_max_power = max_power
            max_power = power_all[i]	#set max_power as the current row frequency
            row = i		#update row number
	
    prev_max_power = max(1, prev_max_power)
    confidence_row = round(max_power / prev_max_power)


# find the maximum power in the column frequencies and the column number

    prev_max_power = 0
    max_power = 0		#initialize max_power=0

    for i in range(4, 8): #loop 4 times from 4>7 (the indecies of the columns)

        if (power_all[i] > max_power):	#if power of the current column frequency > max_power
            prev_max_power = max_power
            # print(f'prev pow {prev_max_power}, max {max_power}')
            max_power = power_all[i]	#set max_power as the current column frequency
            col = i		#update column number
	
    
    prev_max_power = max(1, prev_max_power)
    confidence_col = round(max_power / prev_max_power)

    # if (confidence_row > 100):
    #     print(f'confidence_row {confidence_row}')

    if (power_all[col] < 1e5 and power_all[row] < 1e5):	#if the maximum powers equal zero > this means no signal or inter-digit pause
        new_dig = 1		#set new_dig to 1 to display the next decoded digit


    # print(power_all)
    if ((power_all[col] > 1e5 and power_all[row] > 1e5) and new_dig == 1):	# check if maximum powers of row & column exceed certain threshold AND new_dig flag is set to 1
        # print(power_all)
        # print(f'confidence row {confidence_row} col {confidence_col} power col {power_all[col]} row {power_all[row]}')
        print(row_col[row][col - 4])
        new_dig = 0		# set new_dig to 0 to avoid displaying the same digit again.
    

CHANNELS = 1
FORMAT = pyaudio.paInt16
chunk = N
rate = 16000

p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(2),
                channels=CHANNELS,
                rate=rate,
                input=True,
                output=False,
                frames_per_buffer=chunk)

listen = True
started = False
rel = rate/chunk
frames = []

while listen:
    data = stream.read(chunk)
    decoded = numpy.frombuffer(data, dtype=numpy.int16)
    downscale = decoded >> 8
    # print(decoded)
    avgg = downscale #- numpy.average(downscale)
    # print(downscale)

    # print(downscale[0:2])

    for i in range(0, 8):
        power_all[i] = goertzel(avgg, coeff[i], N)	# call goertzel to calculate the power at each frequency and store it in the power_all array

    # print(power_all)
    # input("waiting...")
    post_test()		# call post test function to validate the data and display the pressed digit if applicable




stream.stop_stream()
stream.close()

p.terminate()