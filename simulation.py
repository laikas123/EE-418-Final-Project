from ids import *
import numpy as np
import matplotlib.pyplot as plt

__author__ = "ee418"


def import_data(file=None):
    with open(file) as f:
        lines = f.readlines()
    data = [float(x.strip()) for x in lines]
    return data


# Plot accumulated offset curves for both state-of-the-art and NTP-based IDSs.
def plot_acc_offsets(ids, mode):
    if mode == 'state-of-the-art':
        # ====================== Start of Your Code =========================
        # Example: Plot accumulated offset curve for 0x184.

        # plt.plot(ids['184-sota'].elapsed_time_sec_hist, ids['184-sota'].acc_offset_us_hist, label='0x184')

        print("DID YOU KNOW I GOT HERE!!!")

        # get the N value (could have grabbed from any IDS since they all use the same N)
        N = ids['184-sota'].N

        # 184 data
        ids_184 = ids['184-sota']
        acc_offset_184 = ids_184.acc_offset_us_hist
        times = ids_184.elapsed_time_sec_hist

        # 3d1 data
        ids_3d1 = ids['3d1-sota']
        acc_offset_3d1 = ids_3d1.acc_offset_us_hist
        times = ids_3d1.elapsed_time_sec_hist

        # 180 data
        ids_180 = ids['180-sota']
        acc_offset_180 = ids_180.acc_offset_us_hist
        times = ids_180.elapsed_time_sec_hist

        fig1 = plt.figure(1)

        plt.plot(times, acc_offset_184, label="184")
        plt.plot(times, acc_offset_3d1, label="3d1")
        plt.plot(times, acc_offset_180, label="180")
        plt.title("Accumulated Offsets State of the Art (N = " + str(N) + ")")
        plt.ylabel('Accumulated Clock Offset (\u03BCs)', color='b')
        plt.xlabel('Time(sec)', color='b')
        plt.legend()
        plt.show()

        # Your code goes here.

        # ====================== End of Your Code =========================
    elif mode == 'ntp-based':
        # ====================== Start of Your Code =========================

        # Your code goes here

        #         plt.plot(ids['184-ntp'].elapsed_time_sec_hist, ids['184-ntp'].acc_offset_us_hist, label='0x184')

        # get the N value (could have grabbed from any IDS since they all use the same N)
        N = ids['184-ntp'].N

        # 184 data
        ids_184 = ids['184-ntp']
        acc_offset_184 = ids_184.acc_offset_us_hist
        times = ids_184.elapsed_time_sec_hist

        # 3d1 data
        ids_3d1 = ids['3d1-ntp']
        acc_offset_3d1 = ids_3d1.acc_offset_us_hist
        times = ids_3d1.elapsed_time_sec_hist

        # 180 data
        ids_180 = ids['180-ntp']
        acc_offset_180 = ids_180.acc_offset_us_hist
        times = ids_180.elapsed_time_sec_hist

        fig1 = plt.figure(2)

        plt.plot(times, acc_offset_184, label="184")
        plt.plot(times, acc_offset_3d1, label="3d1")
        plt.plot(times, acc_offset_180, label="180")
        plt.title("Accumulated Offsets NTP (N = " + str(N) + ")")
        plt.ylabel('Accumulated Clock Offset (\u03BCs)', color='b')
        plt.xlabel('Time(sec)', color='b')
        plt.legend()
        plt.show()

        # ====================== End of Your Code =========================


# TODO: Implement this simulation (N=20)
def simulation_masquerade_attack(mode):
    if mode == 'state-of-the-art':
        # The following code is provided as an example.

        # ECU A (weakly compromised)
        data_184 = import_data('../data/184.txt')

        # ECU B (fully compromised)
        data_3d1 = import_data('../data/3d1.txt')

        # so essentially the data above contains the arrival timestamps of the above messages
        # at the receiver...

        N = 20

        # Construct a new data-set with the first 1000 batches of data_184,
        # followed by 1000 batches of data_3d1. That is, the masquerade
        # attack occurs at the 1001-st batch.
        data_184 = np.asarray(data_184[0:1000 * N]) - data_184[
            0]  # Relative timestamps (hence the subtract first timestamp)
        data_3d1 = np.asarray(data_3d1[0:1000 * N]) - data_3d1[
            0]  # Relative timestamps (hence the subtract first timestamp)

        # ECU A transmits 0x184 normally but is weakly compromised
        # we suspend its transmission just before the 1001st batch
        # then use fully compromised ECU B to transmit spoofed 0x184
        # which for our purpose is just 0x3d1

        # add the spoofed data 1 period (0.1 sec) after last real message
        data = np.append(data_184, data_184[-1] + 0.1 + data_3d1)  # The 1st spoofed message occurs exactly 0.1 sec
        # (the period) after the last legitimate message.

        # instantiate an IDS
        ids = IDS(T_sec=0.1, N=N, mode='state-of-the-art', flag="check")

        # call update for the 2000 batches (half real half spoofed)
        batch_num = 2000
        for i in range(batch_num):
            batch = np.asarray(data[i * N:(i + 1) * N])
            ids.update(batch)

        plt.plot(ids.L_upper_hist, label='Upper Control Limit')
        plt.plot(ids.L_lower_hist, label='Lower Control Limit')
        plt.xlabel('Number of Batches')
        plt.ylabel('Control Limits')
        plt.title('Control Limits for State-of-the-Art IDS')
        plt.legend()
        plt.show()
    elif mode == 'ntp-based':
        # ====================== Start of Your Code =========================

        data_184 = import_data('../data/184.txt')
        data_3d1 = import_data('../data/3d1.txt')

        N = 20

        # Construct a new data-set with the first 1000 batches of data_184,
        # followed by 1000 batches of data_3d1. That is, the masquerade
        # attack occurs at the 1001-st batch.
        data_184 = np.asarray(data_184[0:1000 * N]) - data_184[
            0]  # Relative timestamps (hence the subtract first timestamp)
        data_3d1 = np.asarray(data_3d1[0:1000 * N]) - data_3d1[
            0]  # Relative timestamps (hence the subtract first timestamp)

        # ECU transmits 0x184 normally but is weakly compromised
        # we suspend its transmission just before the 1001st batch
        # then use fully compromised ECU B to transmit spoofed 0x184
        # which for our purpose is just 0x3d1

        # add the spoofed data 1 period (0.1 sec) after last real message
        data = np.append(data_184, data_184[-1] + 0.1 + data_3d1)  # The 1st spoofed message occurs exactly 0.1 sec
        # (the period) after the last legitimate message.

        # instantiate an IDS
        ids = IDS(T_sec=0.1, N=N, mode='ntp-based', flag="check")

        # call update for the 2000 batches (half real half spoofed)
        batch_num = 2000
        for i in range(batch_num):
            batch = np.asarray(data[i * N:(i + 1) * N])
            ids.update(batch)

        plt.plot(ids.L_upper_hist, label='Upper Control Limit')
        plt.plot(ids.L_lower_hist, label='Lower Control Limit')
        plt.xlabel('Number of Batches')
        plt.ylabel('Control Limits')
        plt.title('Control Limits for NTP IDS')
        plt.legend()
        plt.show()

        # ====================== End of Your Code  =========================


# TODO: Implement this simulation (N=20)
def simulation_cloaking_attack(mode):
    if mode == 'state-of-the-art':
        # ====================== Start of Your Code =========================

        # The following code is provided as an example.

        # ECU A (weakly compromised)
        data_184 = import_data('../data/184.txt')

        # ECU C (fully compromised)
        data_180 = import_data('../data/180.txt')

        # so essentially the data above contains the arrival timestamps of the above messages
        # at the receiver...

        N = 20

        delt_T = 0.000029 * -1

        # Construct a new data-set with the first 1000 batches of data_184,
        # followed by 1000 batches of data_180. That is, the masquerade
        # attack occurs at the 1001-st batch.
        data_184 = np.asarray(data_184[0:1000 * N]) - data_184[
            0]  # Relative timestamps (hence the subtract first timestamp)
        data_180 = np.asarray(data_180[0:1000 * N]) - data_180[
            0]  # Relative timestamps (hence the subtract first timestamp)

        # ECU A transmits 0x184 normally but is weakly compromised
        # we suspend its transmission just before the 1001st batch
        # then use fully compromised ECU C to transmit spoofed 0x184
        # which for our purpose is just 0x180, also a delt_T is
        # added to make up for the clock skew difference between
        # Ecu A and Ecu C

        # add the spoofed data 1 period (0.1 sec) after last real message
        data = np.append(data_184,
                         data_184[-1] + 0.1 + delt_T + data_180)  # The 1st spoofed message occurs exactly 0.1 sec
        # (the period) after the last legitimate message.

        # instantiate an IDS
        ids = IDS(T_sec=0.1, N=N, mode='state-of-the-art', flag="check")

        # call update for the 2000 batches (half real half spoofed)
        batch_num = 2000
        for i in range(batch_num):
            batch = np.asarray(data[i * N:(i + 1) * N])
            ids.update(batch)

        plt.plot(ids.L_upper_hist, label='Upper Control Limit')
        plt.plot(ids.L_lower_hist, label='Lower Control Limit')
        plt.xlabel('Number of Batches')
        plt.ylabel('Control Limits')
        plt.title('Control Limits for State-of-the-Art IDS Cloaking')
        plt.legend()
        plt.show()

        # ====================== End of Your Code =========================

    elif mode == 'ntp-based':
        # ====================== Start of Your Code =========================

        # ECU A (weakly compromised)
        data_184 = import_data('../data/184.txt')

        # ECU C (fully compromised)
        data_180 = import_data('../data/180.txt')

        # The data above contains the arrival timestamps of the above messages at the receiver

        N = 20

        delt_T = 0.000029 * -1

        # Construct a new data-set with the first 1000 batches of data_184,
        # followed by 1000 batches of data_180. That is, the masquerade
        # attack occurs at the 1001-st batch.
        data_184 = np.asarray(data_184[0:1000 * N]) - data_184[
            0]  # Relative timestamps (hence the subtract first timestamp)
        data_180 = np.asarray(data_180[0:1000 * N]) - data_180[
            0]  # Relative timestamps (hence the subtract first timestamp)

        # ECU A transmits 0x184 normally but is weakly compromised
        # we suspend its transmission just before the 1001st batch
        # then use fully compromised ECU C to transmit spoofed 0x184
        # which for our purpose is just 0x180, also a delt_T is
        # added to make up for the clock skew difference between
        # Ecu A and Ecu C

        # add the spoofed data 1 period (0.1 sec) after last real message
        data = np.append(data_184,
                         data_184[-1] + 0.1 + delt_T + data_180)  # The 1st spoofed message occurs exactly 0.1 sec
        # (the period) after the last legitimate message.

        # instantiate an IDS
        ids = IDS(T_sec=0.1, N=N, mode='ntp-based', flag="check")

        # call update for the 2000 batches (half real half spoofed)
        batch_num = 2000
        for i in range(batch_num):
            batch = np.asarray(data[i * N:(i + 1) * N])
            ids.update(batch)

        plt.plot(ids.L_upper_hist, label='Upper Control Limit')
        plt.plot(ids.L_lower_hist, label='Lower Control Limit')
        plt.xlabel('Number of Batches')
        plt.ylabel('Control Limits')
        plt.title('Control Limits for NTP IDS Cloaking')
        plt.legend()
        plt.show()

        # ====================== End of Your Code =========================


if __name__ == '__main__':
    # If IDS is correctly implemented, you should be able to run the following code.
    data_184 = import_data('../data/184.txt')
    data_3d1 = import_data('../data/3d1.txt')
    data_180 = import_data('../data/180.txt')

    # by subtracting the first timestamp of the data from all the data
    # the first entry is a 0, and it looks more "human"
    data_184 = np.asarray(data_184) - data_184[0]
    data_3d1 = np.asarray(data_3d1) - data_3d1[0]
    data_180 = np.asarray(data_180) - data_180[0]

    print(data_180[0:20])
    print(data_180[20:40])
    print(data_180[40:60])

    ids = dict()

    N = 20  # Change this to 30 for Task 4
    ids['184-sota'] = IDS(T_sec=0.1, N=N, mode='state-of-the-art')
    ids['184-ntp'] = IDS(T_sec=0.1, N=N, mode='ntp-based')

    ids['3d1-sota'] = IDS(T_sec=0.1, N=N, mode='state-of-the-art')
    ids['3d1-ntp'] = IDS(T_sec=0.1, N=N, mode='ntp-based')

    ids['180-sota'] = IDS(T_sec=0.1, N=N, mode='state-of-the-art', flag=180)
    ids['180-ntp'] = IDS(T_sec=0.1, N=N, mode='ntp-based')

    if N == 20:
        batch_num = 6000
    elif N == 30:
        batch_num = 4000
    else:
        batch_num = 6000

    for i in range(batch_num):
        batch_184 = data_184[i * N:(i + 1) * N]

        ids['184-sota'].update(batch_184)
        ids['184-ntp'].update(batch_184)

        batch_3d1 = data_3d1[i * N:(i + 1) * N]
        ids['3d1-sota'].update(batch_3d1)
        ids['3d1-ntp'].update(batch_3d1)

        batch_180 = data_180[i * N:(i + 1) * N]
        ids['180-sota'].update(batch_180)
        ids['180-ntp'].update(batch_180)

    # Task 2: Plot accumulated offset curves for 0x184, 0x3d1, and 0x180, for the state-of-the-art IDS.
    plot_acc_offsets(ids, "state-of-the-art")  # Uncomment!!!

    # Task 3: Plot accumulated offset curves for 0x184, 0x3d1, and 0x180, for the NTP-based IDS.
    plot_acc_offsets(ids, "ntp-based")  # Uncomment!!!!

    N = 30  # Change this to 30 for Task 4
    ids['184-sota'] = IDS(T_sec=0.1, N=N, mode='state-of-the-art')
    ids['184-ntp'] = IDS(T_sec=0.1, N=N, mode='ntp-based')

    ids['3d1-sota'] = IDS(T_sec=0.1, N=N, mode='state-of-the-art')
    ids['3d1-ntp'] = IDS(T_sec=0.1, N=N, mode='ntp-based')

    ids['180-sota'] = IDS(T_sec=0.1, N=N, mode='state-of-the-art', flag=180)
    ids['180-ntp'] = IDS(T_sec=0.1, N=N, mode='ntp-based')

    if N == 20:
        batch_num = 6000
    elif N == 30:
        batch_num = 4000
    else:
        batch_num = 6000

    for i in range(batch_num):
        batch_184 = data_184[i * N:(i + 1) * N]

        ids['184-sota'].update(batch_184)
        ids['184-ntp'].update(batch_184)

        batch_3d1 = data_3d1[i * N:(i + 1) * N]
        ids['3d1-sota'].update(batch_3d1)
        ids['3d1-ntp'].update(batch_3d1)

        batch_180 = data_180[i * N:(i + 1) * N]
        ids['180-sota'].update(batch_180)
        ids['180-ntp'].update(batch_180)

    #     # Task 4: Change N to 30, and repeat Tasks 2 and 3.
    plot_acc_offsets(ids, "state-of-the-art")  # Uncomment!!!!
    plot_acc_offsets(ids, "ntp-based")  # Uncomment!!!!

    #     # Task 5: Simulate the masquerade attack, and plot upper/lower control limits.
    simulation_masquerade_attack("state-of-the-art")
    simulation_masquerade_attack("ntp-based")

    #     # Task 6: Simulate the cloaking attack, and plot upper/lower control limits.
    simulation_cloaking_attack("state-of-the-art")
    simulation_cloaking_attack("ntp-based")