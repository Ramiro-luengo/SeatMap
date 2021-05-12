import xml.etree.ElementTree as ET
import argparse

class XML_parser():
    
    @staticmethod
    def parse(file):
        with open(file,'r') as f:
            return
        

if __name__ == '__main__':
    args = None
    parser =  argparse.ArgumentParser()
    parser.add_argument('file',help='XML file to parse',type=str)

    try:
        args = parser.parse_args()
        file = args.file
    except Exception as e:
        print("Wrong arguments, check syntax.\n")
        print("Error: " ,e)

    
    if file:
        XML_parser().parse(file)

