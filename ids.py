"""
This implements both state-of-the-art and NTP-based IDSs.
"""
import numpy as np

__author__ = "Hunter North, Ethan Sepa, and Logan Aikas"

class IDS:
    def __init__(self, T_sec, N, mode, flag = None):
        if (mode != 'state-of-the-art') & (mode != 'ntp-based'):
            raise ValueError('Unknown IDS mode')

        self.mode = mode

        self.k = 0  # Current batch
        self.N = N  # Batch size
        self.T_sec = T_sec # Nominal period in sec

        self.mu_T_sec = 0            # Average inter-arrival time in the current batch (sec)
        self.batch_end_time_sec = 0  # End time of every batch (sec)
        self.init_time_sec = 0       # Arrival time of the 1st message in the 2nd batch (sec)
        self.elapsed_time_sec = 0    # Elapsed time since the 1st message in the 2nd batch (sec)

        self.acc_offset_us = 0  # Most recent accumulated offset (us)
        self.avg_offset_us = 0  # Most recent average offset (us)
        self.skew = 0           # Most recent estimated skew (ppm)
        self.P = 1              # Parameter used in RLS <-- the algorithm we use

        #lists to hold history
        self.mu_T_sec_hist = []
        self.batch_end_time_sec_hist = []
        self.elapsed_time_sec_hist = []
        self.acc_offset_us_hist = []
        self.avg_offset_us_hist = []
        self.skew_hist = []
        self.error_hist = []

        # CUSUM
        self.is_detected = 0

        self.n_init = 50  # Number of error samples for initializing mu_e and sigma_e
        self.k_CUSUM_start = self.n_init + 1  # CUSUM starts after mu and sigma are initialized

        self.Gamma = 5  # Control limit threshold
        self.gamma = 4  # Update threshold
        self.kappa = 8  # Sensitivity parameter in CUSUM

        self.L_upper = 0  # Most recent upper control limit
        self.L_lower = 0  # Most recent upper control limit
        self.e_ref = []   # Reference (un-normalized) error samples; used to compute mu_e and sigma_e

        self.L_upper_hist = []
        self.L_lower_hist = []

        self.flag = flag

    # `a` is a 1-by-N vector that contains arrival timestamps of the latest batch.
    #this function is the work horse that calls all the helper functions
    def update(self, a):
        if len(a) != self.N:
            raise ValueError('Inconsistent batch size')

        #increment the batch number
        self.k += 1

        #add the last timestamp in this batch
        #to the history of all "end timestamps" for batches
        self.batch_end_time_sec_hist.append(a[-1])

        #if we are on the first batch
        if self.k == 1:     # Initialize something in the first batch
            if self.mode == 'state-of-the-art':
                self.mu_T_sec = np.mean(a[1:] - a[:-1])
                if(self.flag == 180):
                    print("MU IS:", self.mu_T_sec)
            return

        # CIDS officially starts from the second batch
        if self.k == 2:
            #the intial time = 0 is the first timestamp of the second batch
            self.init_time_sec = a[0]

        if self.k >= 2:
            curr_avg_offset_us, curr_acc_offset_us = self.estimate_offset(a)
            curr_error_sample = self.update_clock_skew(curr_avg_offset_us, curr_acc_offset_us)

            #curr_error_sample is the e[k] basically error between actual offset and predicted offset
            self.update_cusum(curr_error_sample)
            if(self.k <= 3 and self.mode == 'state-of-the-art' and self.flag == 180):
                print(curr_avg_offset_us)

    def estimate_offset(self, a):
        if len(a) != self.N:
            raise ValueError('Inconsistent batch size')

        # Get total time of batch
        self.elapsed_time_sec = a[-1] - self.init_time_sec
        #append the elapsed time to history
        self.elapsed_time_sec_hist.append(self.elapsed_time_sec)

        # Save the previous mu_T value
        prev_mu_T_sec = self.mu_T_sec

        #calculate the average of the difference between consecutive timestamps in the batch
        self.mu_T_sec = np.mean(a[1:] - a[:-1])

        # Append the average to the history
        self.mu_T_sec_hist.append(self.mu_T_sec)
        # Save the previous accumulated offset
        prev_acc_offset_us = self.acc_offset_us

        # Arrival timestamp of the last message in the previous batch
        a0 = self.batch_end_time_sec_hist[-2]   # [-2] is the second to last item
        # Initialize average and accumulated offsets to zero
        curr_avg_offset_us, curr_acc_offset_us = 0, 0

        #define N to be the length of a (the batch size) <--- could also be self.N
        N = self.N

        if self.mode == 'state-of-the-art':
            # ====================== Start of Your Code =========================
            # Compute curr_avg_offset
            a1 = a[0]
            #iterate from 2 to N
            for i in range(2, N+1):
                curr_avg_offset_us += (a[i-1]-(a1+(i-1)*prev_mu_T_sec)) #changing a[i-1] to a[i]
            #get the average of the sum
            curr_avg_offset_us *= 1/(N-1)

            # Compute curr_avg_offset_us
            curr_acc_offset_us = prev_acc_offset_us + abs(curr_avg_offset_us)

            # Print outputs for the first 4 batches if print flag is on
            if(self.k <= 3 and self.mode == 'state-of-the-art' and self.flag == 180):
                print(curr_avg_offset_us, "better", a1)
                print(a)
            # ====================== End of Your Code =========================

        elif self.mode == 'ntp-based':
            # ====================== Start of Your Code =========================
            # Compute curr_avg_offset_us
            curr_avg_offset_us = self.T_sec - (a[N-1]-a0)/N
            # Compute curr_acc_offset_us for NTP-based IDS
            curr_acc_offset_us = prev_acc_offset_us + N*curr_avg_offset_us
            # ====================== End of Your Code =========================

        return curr_avg_offset_us, curr_acc_offset_us

    def update_clock_skew(self, curr_avg_offset_us, curr_acc_offset_us):
        #S[k-1]
        prev_skew = self.skew
        #P[k-1]
        prev_P = self.P
        #t[k]
        time_elapsed_sec = self.elapsed_time_sec
        #e[k]
        curr_error = curr_acc_offset_us - prev_skew * time_elapsed_sec
        #lambda
        l = 0.9995

        # ====================== Start of Your Code =========================
        # RLS algorithm
        # Inputs:
        #   t[k] -> time_elapsed_sec
        #   P[k-1] -> prev_P
        #   S[k-1] -> prev_skew
        #   e[k] -> curr_error
        #   lambda -> l
        #
        # Outputs:
        #   P[k] -> curr_P
        #   S[k] -> curr_skew
        #
        l_inv = (l**(-1))

        gain_numerator = l_inv*prev_P*time_elapsed_sec
        gain_denominator = 1+l_inv*((time_elapsed_sec**2)*prev_P)
        gain = gain_numerator/gain_denominator

        curr_P = l_inv*(prev_P - gain*time_elapsed_sec*prev_P)
        curr_skew = prev_skew+gain*curr_error
        # ====================== End of Your Code =========================

        # Update the state of IDS
        self.avg_offset_us = curr_avg_offset_us
        self.acc_offset_us = curr_acc_offset_us
        self.skew = curr_skew
        self.P = curr_P

        self.avg_offset_us_hist.append(curr_avg_offset_us)
        self.acc_offset_us_hist.append(curr_acc_offset_us)
        self.skew_hist.append(curr_skew)
        self.error_hist.append(curr_error)

        return curr_error

    def update_cusum(self, curr_error_sample):
        # Wait until errors of 51 batches have been collected to begin CUSUM
        if self.k <= self.k_CUSUM_start:
            self.e_ref.append(curr_error_sample) #list containing all unnormalized error samples
            return

        # Save the previous upper and lower values
        prev_L_upper = self.L_upper
        prev_L_lower = self.L_lower

        # Compute mu_e and sigma_e
        e_ref_arr = np.asarray(self.e_ref) #get the unnormalized error samples as a numpy array
        mu_e = np.mean(e_ref_arr) #calculate mean
        sigma_e = np.std(e_ref_arr) #calculate standard deviation

        # Set the sensitivity parameter
        kappa = self.kappa

        # ====================== Start of Your Code =========================
        # Calculate normalized error
        normalized_error = (curr_error_sample - mu_e)/sigma_e

        # Calculate the new upper and lower values
        curr_L_upper = max(0, prev_L_upper + normalized_error - kappa)
        curr_L_lower = max(0, prev_L_lower - normalized_error - kappa)
        # ====================== End of Your Code =========================

        # Unnormalized error gets stored if less than the threshold gamma
        if (curr_L_upper > self.Gamma) | (curr_L_lower > self.Gamma):
            self.is_detected = True
            if(self.flag == "check"):
                print("ERROR DETECTED", self.mode, "k = ", self.k)

        # Store valid (un-normalized) error sample
        if abs(normalized_error) < self.gamma:
            self.e_ref.append(curr_error_sample)

        # Update the state of CUSUM
        self.L_upper = curr_L_upper
        self.L_lower = curr_L_lower
        self.L_upper_hist.append(curr_L_upper)
        self.L_lower_hist.append(curr_L_lower)