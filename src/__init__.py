import argparse

def parse_args():
    """
    A function to create an argument parser. The arguments will be determined by the inputs given by the user.
    They will be used to determine how the function runs and what it returns.
    """
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-loc",
        "--location",
        type=str,
        help="The location where the UV index should be calculated for.",
        required=True
    )
    
    parser.add_argument(
        "-curr",
        "--current",
        help="Whether the current UV index should be returned.",
        required=False,
        action="store_true"
    )
    
    parser.add_argument(
        "-time",
        help="The time for which the UV index should be calculated. Should be in the format HH:MM.",
        required=False,
        type=str
    )
    
    parser.add_argument(
        "-start",
        "--start_time",
        help="The starting datetime for calculating UV dosage for a period. Should be in the format dd/mm/yy HH:MM.",
        type=str,
        required=False
    )
    
    parser.add_argument(
        "-end",
        "--end_time",
        help="The end datetime for calculating UV dosage for a period. Should be in the format dd/mm/yy HH:MM.",
        type=str,
        required=False
    )
    
    parser.add_argument(
        "-lat",
        "--latitude",
        help="The latitude of the location.",
        type=float,
        required=False
    )
    
    parser.add_argument(
        "-long",
        "--longitude",
        help="The longitude of the location.",
        type=float,
        required=False
    )
    
    return parser.parse_args()