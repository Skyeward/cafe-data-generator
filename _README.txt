Cafe Data Generator is a program for generating random sales data for one day of a virtual cafe. It is based on an original version by IW.


There are [or will be] two versions:
 - csv_generator.py will generate a .csv file intended to emulate the original IW cafe data generator as accurately as possible.
 
 - [coming soon!] will generate a .csv file with new custom settings intended to simplify and remove bugs from the original version.


NOTES FOR BOTH VERSIONS:
 - Random names are generated from an API that is limited to 20,000 name requests per minute. This will limit you to running the program - and thus generating a .csv file - more than ~10 times a minute approximately.
 
 - The API can occasionally fail, if not due to over-requesting then simply bandwidth limitations. Try again in a short while if this is the case.
 
 - If all names are returning "Alan Smithee" in the csv file, set debug_mode to False in the get_random_names(order_count, True) call in generate_csv().
 
 
IF USING EMULATED_CSV_GENERATOR:
Some notes to bear in mind if using the version intended to emulate the IW original:

 - Names are filtered to not contain any special characters such as accented letters.
 
 - In the IW version, drinks without a Large/Regular size have a leading space before their name. This is carried over to the emulator. Examples of that formatting:
 --- "Large tea, Large coffee"
 --- " Tea,  Coffee"
 
 - Hot chocolate has a bug where it can appear both as a sized Regular/Large hot chocolate (costing 2.20/2.90 respectively) or an unsized Hot chocolate (costing 1.40). This has been carried over to the emulator.
 
 - In the config, 'frequency' values are the near-exact order counts for that hour period. However, despite frequency parameters being listed as each hour from the open time (eg with an opening time of 814, times would continue as 914, 1014 etc) the actual times these map to on the csv begin at o'clock after the hour. This is partially carried over to the emulator.
 
 - Since the hour periods in the csv use the frequency value from the previous hour, AND frequencies are only defined an hour AFTER opening, there is are no defined frequency values for either ~8-9am sales or ~9-10am sales. Instead, they use the value from the final frequency slot of the day. Due to a bug in the original, the one exception for an 8am-5pm cafe is that the 4pm sales use the ~4pm frequency value, not the ~3pm frequency value. As such, the ~3pm value in the original cofig is never used. This has NOT been carried over to the emulator - instead, the ~4pm frequency value is unused at the end of the day (but is still used by the first two hours as mentioned previously)
 
 - I have not been able to establish what determines the number of drinks per order in the IW original. They appear to be non-homogenous, and yet there is no distinct pattern. The emulator gives even probability weighting to any number of drinks between 1-5.
 
 - Despite some menu probability weighting in the config matching the csv files precisely, some are reduced by a multiple of 15. (15, 30 and 60 have been observed). I have not determined the cause of this behaviour (and it may be a bug?) and so the emulator simply matches all menu probability weightings exactly. 
 
 -   CONFIG  -> CSV VALUE - EXAMPLE FROM ORIGINAL IW (note the hour lag, and the missing 3pm value in the csv)
 - 0800:     -> 53 (using the 64 value from 4pm but truncated by not having a full hour)
 - 0900:  39 -> 64
 - 1000: 110 -> 39
 - 1100:  19 -> 110
 - 1200:  48 -> 19
 - 1300:  96 -> 48
 - 1400:  94 -> 96
 - 1500:  91 -> 94
 - 1600:  64 -> 64
 
  -   CONFIG  -> CSV VALUE - EXAMPLE FROM EMULATED VERSION (note the use of the 3pm value)
 - 0800:     -> 53 (using the 64 value from 4pm but truncated by not having a full hour)
 - 0900:  39 -> 64
 - 1000: 110 -> 39
 - 1100:  19 -> 110
 - 1200:  48 -> 19
 - 1300:  96 -> 48
 - 1400:  94 -> 96
 - 1500:  91 -> 94
 - 1600:  64 -> 91
 
 
IF USING [coming soon!]
 - You're clearly a time-traveller, I haven't made that one yet