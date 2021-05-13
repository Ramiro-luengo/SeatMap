import xml.etree.ElementTree as ET
import argparse
import json
from pathlib import Path

class Row():
    def __init__(self,row_number,seats=None):
        self._row_number = row_number
        self._seats = seats

    @property
    def row_number(self):
        return self._row_number
    
    @row_number.setter
    def row_number(self,new_number):
        self._seats = new_number

    def add_seat(self,seat):
        if self._seats:
            self._seats.append(seat)
        else:
            self._seats = [seat]
    
    def get_json(self):
        return {'RowNumber' : self.row_number, 'Seats' : self._seats}

class Seat():
    def __init__(self,element_type,_id,availability,cabin_type,is_preferred=False,price=None):
        self._element_type = element_type
        self._id = _id
        self._availability = availability
        self._cabin_type = cabin_type
        self._is_preferred = is_preferred
        self._price = price

    def get_json(self):
        data = {
                'Element Type': self._element_type,
                'Seat Id': self._id,
                'Cabin Class': self._cabin_type,
                'Availability': self._availability,
            }

        if self._price and self._is_preferred:
            data.update({'IsPreferred' : self._is_preferred,'Price' : self._price})
        
        return data

class XML_parser():
    
    def get_root(self,file):
        try:
            tree = ET.parse(file)
        except:
            new_path = Path(__file__).parent / file
            tree = ET.parse(new_path)

        return tree.getroot()

    def find_index(self,list,number):
        for idx,value in enumerate(list):
            if value.row_number == number:
                return idx
        
        return None

    def parse_seatmap1(self,root):
        seatmap_xml_responses = root.iter('{http://www.opentravel.org/OTA/2003/05/common/}SeatMapResponse')
        rows = []
        for item in seatmap_xml_responses:
            seat_map_details = item[1]
            for cabin in seat_map_details:
                for row in cabin:
                    row_number = int(row.attrib.get('RowNumber'))
                    cabin_type = row.attrib.get('CabinType')
                    rows.append(Row(row_number))
                    for seat in row:
                        seat_info = seat.findall("{http://www.opentravel.org/OTA/2003/05/common/}Summary")
                        if seat_info:
                            seat_info = seat_info[0]
                            seat_id = seat_info.attrib.get('SeatNumber')
                            availability = not json.loads(seat_info.attrib.get('OccupiedInd'))
                            elemnt_type = 'Seat'
                            # The seatmap1 json doesn't have a Seat Price in the xml.
                            # Just some prices for preferred seats.
                            
                            preferred = seat.findall("{http://www.opentravel.org/OTA/2003/05/common/}Service")
                            is_preferred = False
                            if preferred:
                                is_preferred = True
                                preferred = preferred[0]
                                if preferred.attrib.get('CodeContext') == 'Preferred':
                                    # This is a preferred seat, which costs more.
                                    price = int(preferred[0].attrib.get('Amount'))
                            if is_preferred:
                                seat = Seat(elemnt_type,seat_id,availability,cabin_type,is_preferred=is_preferred,price=price)
                            else:
                                seat = Seat(elemnt_type,seat_id,availability,cabin_type)
                            
                            row_index = self.find_index(rows,row_number)
                            # print(row_index)   
                            rows[row_index].add_seat(seat.get_json())

        rows = list(map(lambda r: r.get_json(),rows))
        # print(rows)
        return {'Rows' : rows}
    
    def parse_seatmap2(self,root):
        return

    def parse(self,file):
        filename = file.split('.')[0]

        root = self.get_root(file)
        
        if filename == 'seatmap1':
            seatmap = self.parse_seatmap1(root)
        else:
            seatmap = self.parse_seatmap2(root)
        
        self.generate_output(seatmap,filename)

    def generate_output(self,json_data,filename):
        with open(filename + '.json','w') as f:
            json.dump(json_data,f, indent=4)
        
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
        parser = XML_parser()
        parser.parse(file)

