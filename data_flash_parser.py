import argparse
from pymavlink import DFReader

VALIDATORS = [{"name": "Motor Performance Analyzer", 
               "dependent_message_types": ["MOTB"],
               "handler":"analyze_motor_performance", 
               "report":{"messages_processed": 0, "issues_found": 0}}
            ]

log_file_path = '/home/simran/Work/AERPAW/DataFlashParser/log_sample.bin' 

def analyze_motor_performance(message, report):
    if message_type == 'MOTB':
        report["messages_processed"] += 1

def call_validator(message):
    for validator in VALIDATORS:
        if message.get_type() in validator["dependent_message_types"]:
            handler = globals().get(validator["handler"])
            report = globals().get("report")
            if handler:
                handler(message, report)

def print_reports():
    print("Reports:")
    print("-" * 40)
    for validator in VALIDATORS:
        if "report" in validator:
            print(f"{validator['name']} Report:")
            print(validator["report"])
    
unique_message_types = []
message_counts = {}
try:
    reader = DFReader.DFReader_binary(log_file_path)

    while True:
        message = reader.recv_match()
        if message is None:
            break

        call_validator(message)

        message_type = message.get_type()
        if message_type not in unique_message_types:
            unique_message_types.append(message_type)
            message_counts[message_type] = 0
        
        # Conditions for other message types
        if message_type == 'ATT':
            pass
            # print(f"ATT: TimeUS={message.TimeUS}, Roll={message.Roll}, Pitch={message.Pitch}, Yaw={message.Yaw}")
        elif message_type == 'GPS':
            pass
            # print(f"GPS: TimeUS={message.TimeUS}, Lat={message.Lat}, Lng={message.Lng}, Alt={message.Alt}")
        elif message_type == 'TRST':
            pass
            input(f"TRST: {message}")
        elif message_type == 'POS':
            pass
        message_counts[message_type] += 1

    print("Unique message types encountered:")
    for msg_type in unique_message_types:
        print(f"{msg_type} Count: {message_counts[msg_type]}")
        print("-" * 40)

    print_reports()
except Exception as e:
    print(f"An error occurred: {e}")
