debug = False #Skip login

max_thread = True #False means there is no upper limit to the number of threads. True means that the program will limit the number of threads we create. True saves resources but takes more time.
thread_limit = 4 #if max_thread is true the program will only create this many threads

default_dids_per_page = 100 #Max 100
default_request_per_page = 5000 #Max 5000
default_trunks_per_page = 50 #Max 200

inboud_charge_rate = 0.0110
outbound_charge_rate = 0.0220
