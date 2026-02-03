#!/usr/bin/env python3
import make_call_simple_survey as survey_mc_module
from call_id_tracker import CallIdTracker
import local_stt as lstt
import time
import os

CALLS_ANSWERS_DIR = "calls_answers"

def clear_active_calls(active_calls):
    """Remove call_ids from active_calls if their answer file exists (indicating completion)"""
    remaining_calls = []
    for call_id in active_calls:
        if not os.path.exists(f"./calls_answers/{call_id}_call_done"):
            remaining_calls.append(call_id)
    return remaining_calls

def wait_for_active_calls(active_calls, max=0):
    """Wait until all call_ids in active_calls have their answer files created"""
    strr = f"Waiting Active calls."
    count = 0
    while len(active_calls) > max:
        time.sleep(1)
        active_calls = clear_active_calls(active_calls)
        print(strr+"."*(count%3)+"   ", end="\r")
        count += 1

    print(" " * (len(strr) + 4), end="\r")  # Clear the line

# change the folowing in the future to run campaigns!
def get_numbers():
    return ["0546844668", "0542325811"]
def get_source_number():
    return "0534540615"
def get_max_concurrent_calls():
    return 10

def main():
    numbers = get_numbers()
    source_number = get_source_number()
    max_calls = get_max_concurrent_calls()

    os.makedirs(CALLS_ANSWERS_DIR, exist_ok=True)

    tracker = CallIdTracker()

    active_calls = []

    for number in numbers:
        wait_for_active_calls(active_calls, max=max_calls - 1)

        call_id = tracker.get_next()

        # clean leftovers (safety)
        survey_mc_module.clear_call_files(call_id)

        # make the call
        survey_mc_module.make_call(number, source_number, call_id)

        print(f"Started call to {number} with call_id {call_id}")
        active_calls.append(call_id)

    wait_for_active_calls(active_calls)

    print("All calls completed.")

if __name__ == "__main__":
    #test()
    main()