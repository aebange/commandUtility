# Filename:  commandUtility.py
# Author:    Alex Bange
# Purpose:
#   To automatically clean all of the files out of the temp directories
#   To automatically run a speed-test of the local network
#
# Usage
#   commandUtility.py -# #
#
# Assumptions
#   A) python is in the PATH
#   B) commandUtility.py is in the PATH
#   C) winshell, argparse, time, sys, os, and speedtest-cli modules are installed
from os import listdir, unlink
from sys import exit
from winshell import recycle_bin
from time import perf_counter
from argparse import ArgumentParser
from speedtest import Speedtest
from pgeocode import Nominatim


parser = ArgumentParser()
parser.add_argument("-c", "--trgt", help="cleans files from temporary target directories")
parser.add_argument("-p", "--ping", action='store_true', help="tests the local network connection speeds")
parser.add_argument("-z", "--zip", help="provides location data for a specified zip-code in the US")
args = parser.parse_args()

targetDirectories = ['C:\\Windows\\Downloaded Program Files', 'C:\\Windows\\temp',
                     'C:\\Users\\Alex Bange\\AppData\\Local\\Temp']
targetWindowsDirectories = [targetDirectories[0], targetDirectories[1]]
targetRoamingDirectories = [targetDirectories[2]]


# SYSTEM CLEANER FUNCTIONS --------------------------------------------------------------------------------------------


# Empties the windows recycle bin (except when there's nothing inside)
def clean_recycle_bin():
    try:
        recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        print("Removed files from recycle bin")
    except:
        # The recycle bin is empty, normally wouldn't leave 'except' open-ended but I can't identify the error type
        pass


# Shortens the printed path to each target file for cleaner display
def passed_output_handler(local_folder):
    try:
        local_pretty_folder = local_folder.rsplit('Bange', 1)[1]
        return local_pretty_folder
    except IndexError:
        return local_folder


# Cleans the files out of the recycle bin and temporary directories (depending on provided arguments)
def clean_directory(local_trgt):
    local_start = perf_counter()
    if local_trgt == 'a':
        local_target_directory = targetDirectories
    elif local_trgt == 'w':
        local_target_directory = targetWindowsDirectories
    elif local_trgt == 'r':
        local_target_directory = targetRoamingDirectories
    else:
        print("ERROR: Invalid value passed to 'clean_directory' function.")
        exit()
    local_count = 0
    file_count = 0
    for folder in local_target_directory:
        local_cwd = folder
        for filename in listdir(folder):
            local_path = (local_cwd + '\\' + filename)
            try:
                unlink(local_path)
                print("Removed {} from {}".format(filename, passed_output_handler(folder)))
                file_count += 1
            except PermissionError:
                print("Passed {} from {}, still in use".format(filename, passed_output_handler(folder)))
        local_count += 1
    if local_trgt == 'a' or local_trgt == 'w':
        clean_recycle_bin()
    local_end = round((perf_counter() - local_start), 2)
    print("COMPLETE: Cleared {} files in {} seconds.".format(file_count, local_end))


# NETWORK SPEED-TEST FUNCTIONS ----------------------------------------------------------------------------------------


# Runs a test of the current internet connection and returns the download/upload speed and ping connection to server
def check_speed():
    local_st = Speedtest()
    local_servers = []
    print("Performing network operations...")
    local_st.get_servers(local_servers)
    local_st.get_best_server()
    local_st.download()
    local_st.upload()
    local_st_results = local_st.results.dict()
    local_download_speed = bps_to_mbps(local_st_results['download'])
    local_upload_speed = bps_to_mbps(local_st_results['upload'])
    local_ping = local_st_results['ping']
    print("COMPLETE: Ping: {}ms, Download: {}Mbps, Upload: {}Mbps.".format(local_ping, local_download_speed, local_upload_speed))
    exit()


# Converts the speed-test output in bps to Mbps
def bps_to_mbps(local_bps):
    local_mbps = round(local_bps / 1000 / 1000, 1)
    return local_mbps


# WEATHER DATA FUNCTIONS ---------------------------------------------------------------------------------------------


# Convert a zip code into lat/long coords to be passed to weather lib
def zip_to_coords(local_zip_code, local_country='us'):
    # This is very slow and should only be called when necessary
    print("Retrieving location data...")
    local_nomi = Nominatim(local_country)
    local_location_details = local_nomi.query_postal_code(local_zip_code)
    print("IDENTIFIED: {}, {} - located at ({}, {}) in {}.".format(
        local_location_details[2], local_location_details[4], local_location_details[9],
        local_location_details[10], local_location_details[1]))
    # These should always work presuming the index for the pandas.core.series.Series object type isn't changed
    local_latitude = local_location_details[9]
    local_longitude = local_location_details[10]
    local_coords = [local_latitude, local_longitude]
    return local_coords


def get_weather_data():
    # TODO: Make this lol
    pass

# PROGRAM ROUTINE ----------------------------------------------------------------------------------------------------


def main():
    # Checks to see which argument was provided for -c and executes the cleaning function accordingly
    if args.trgt:
        if args.trgt == "a":
            # Clean all directories
            print("Cleaning all directories...")
            clean_directory(args.trgt)
        elif args.trgt == "w":
            # Clean windows directories
            print("Cleaning windows directories...")
            clean_directory(args.trgt)
        elif args.trgt == "r":
            # Clean roaming directories
            print("Cleaning roaming directories...")
            clean_directory(args.trgt)
        else:
            print("Unrecognized command argument")
            print("    'a' cleans all files from all temp directories and the recycle bin")
            print("    'w' cleans all files from windows temp directories and recycle bin")
            print("    'r' cleans all files from roaming temp directories")
    # Provides location data for a specified zip code
    if args.zip:
        zip_to_coords(str(args.zip))
    # Checks to see if the ping argument was provided
    if args.ping:
        check_speed()


main()

# Python script ends here
exit(0)
