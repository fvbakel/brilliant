import math
import argparse
import xml.etree.ElementTree as ET
import copy


class GpxReducer:

    def __init__(self,filename:str):
        self.max_name_size = 13
        self.filename=filename
        self.tree = ET.parse(filename)
        self.init_namespace()
        self.get_stats()

    def init_namespace(self):
        ns_gpx = 'http://www.topografix.com/GPX/1/1'
        self.namespaces = dict()
        self.namespaces['gpx'] = ns_gpx
        ET.register_namespace('', ns_gpx)
    
    def _get_out_filename(self,postfix:str):
        return self.filename.replace(".gpx","") + f"{postfix}.gpx"

    def _count(self,xpath):
        root = self.tree.getroot()
        return len(root.findall(xpath,self.namespaces))

    def get_stats(self):
        self.trk_count = self._count('./gpx:trk')
        self.seg_count = self._count('./gpx:trk/gpx:trkseg')
        self.point_count = self._count('./gpx:trk/gpx:trkseg/gpx:trkpt')

    def get_new_tree(self):
        root = self.tree.getroot()
        new_root = ET.Element('gpx',root.attrib)
        tree = ET.ElementTree(new_root)
        return tree

    def print_stats(self):
        print(f"Tracks      : {self.trk_count}")
        print(f"Segments    : {self.seg_count}")
        print(f"Points      : {self.point_count}")

    def split_segments(self):
        if self.seg_count == 1:
            print('There are no segments, no split required')
            return

        if self.seg_count == 1:
            print('There is only one segment, no split required')
            return

        print(f"Splitting existing {self.seg_count} segments in separate files.")
        root = self.tree.getroot()
        nr = 1
        for trk in root:
            new_trk = ET.Element('trk',trk.attrib)
            names = trk.findall('./gpx:name',self.namespaces)
            descs = trk.findall('./gpx:desc',self.namespaces)

            seg_index = 0
            for seg in trk.findall('./gpx:trkseg',self.namespaces):
                tree = self.get_new_tree()
                seg_root = tree.getroot()
                seg_trk = copy.copy(new_trk)
                seg_trk.append(copy.copy(names[seg_index]))
                seg_trk.append(copy.copy(descs[seg_index]))
                seg_trk.append(copy.deepcopy(seg))
                seg_root.append(seg_trk)
                tree.write(self._get_out_filename(f'_seg_{nr}'),xml_declaration=True)
                seg_index += 1
                nr += 1

    def split_files(self,max:int):
        if self.seg_count > 1:
            print(f"Found {self.seg_count} segments, use split_segments first" )
            return

        nr_of_files = math.ceil(self.point_count / max )
        
        if nr_of_files < 2 :
            print(f"No split required, number of points {self.point_count} is smaller than {max}")
            return

        print(f"Will create {nr_of_files} files with maximum of {max} points per file")

        root = self.tree.getroot()

        trk = root.find('./gpx:trk',self.namespaces)
        name = trk.find('./gpx:name',self.namespaces)
        desc = trk.find('./gpx:desc',self.namespaces)
        seg =  trk.find('./gpx:trkseg',self.namespaces)

        def make_new_track(file_nr:int):
            tmp_tree = self.get_new_tree()
            tmp_root = tmp_tree.getroot()
            tmp_trk = ET.Element('trk',trk.attrib)
            tmp_root.append(tmp_trk)

            new_name = copy.copy(name)
            new_name.text = f'{new_name.text[0:self.max_name_size-2]}{file_nr:2}'
            tmp_trk.append(new_name)
            tmp_trk.append(copy.copy(desc))
            new_seg = ET.Element('trkseg',seg.attrib)
            tmp_trk.append(new_seg)
            return [tmp_tree, new_seg]

        file_nr = 1
        new_tree:ET.ElementTree
        new_seg:ET.Element 
        new_tree, new_seg= make_new_track(file_nr)
        
        for index,point in enumerate(seg,start=1):
            new_point = copy.copy(point)
            new_seg.append(new_point)
            if (index % max) == 0:
                new_tree.write(self._get_out_filename(f'_{file_nr}'),xml_declaration=True)
                file_nr += 1
                new_tree,new_seg = make_new_track(file_nr)
            
        if (index % max) != 0:
            new_tree.write(self._get_out_filename(f'_{file_nr}'),xml_declaration=True)

    def reduce(self,max:int):
        to_reduce = self.point_count - max 
        
        if to_reduce < 1 :
            print(f"No reduce required, number of points is {self.point_count} while maximum is {max}")
            return

        print(f"Need to reduce from {self.point_count} to {max}")
        
        #remove_every = math.ceil(self.point_count / to_reduce )
        keep_every = math.ceil(self.point_count / max )
        print(f"Keep every {keep_every}th point")
    
        root = self.tree.getroot()

        trk = root.find('./gpx:trk',self.namespaces)
        name = trk.find('./gpx:name',self.namespaces)
        desc = trk.find('./gpx:desc',self.namespaces)
        seg =  trk.find('./gpx:trkseg',self.namespaces)

        new_tree = self.get_new_tree()
        new_root = new_tree.getroot()
        tmp_trk = ET.Element('trk',trk.attrib)
        new_root.append(tmp_trk)
        tmp_trk.append(copy.copy(name))
        tmp_trk.append(copy.copy(desc))
        new_seg = ET.Element('trkseg',seg.attrib)
        tmp_trk.append(new_seg)
        
        removed = 0
        for index,point in enumerate(seg):
            if (index % keep_every) == 0 or removed >= to_reduce:
                new_point = copy.copy(point)
                new_seg.append(new_point)
            else:
                removed += 1
        print(f"Removed {removed} points")
        new_tree.write(self._get_out_filename(f'_reduced'),xml_declaration=True)
    
    def automatic(self,max:int):
        print('Automatic mode')
        if self.point_count <= max:
            print(f"No reduce required, number of points is {self.point_count} while maximum is {max}")
            return
        if self.seg_count > 1:
            self.split_segments()
            return
        self.split_files(max)

def main():
    parser = argparse.ArgumentParser(description="Reduce the number of points in a GPX track")
    parser.add_argument('-m','--max', help='Max number of lines in output', required=False,type=int,default=500)
    parser.add_argument('-s','--segments', help='Split the existing segments in the file to separate files',action=argparse.BooleanOptionalAction,required=False,type=bool,default=False)
    parser.add_argument('-r','--reduce', help='Drop points to achieve the max number of points',action=argparse.BooleanOptionalAction,required=False,type=bool,default=False)
    parser.add_argument('-p','--print', help='Print only statistics of the GPX file',action=argparse.BooleanOptionalAction,required=False,type=bool,default=False)
    parser.add_argument('-a','--automatic', help='Automatic handle based on statistics of the GPX file',action=argparse.BooleanOptionalAction,required=False,type=bool,default=False)
    parser.add_argument('filename', help='Input filename', type=str)

    args = parser.parse_args()

    reducer = GpxReducer(args.filename)
    reducer.print_stats()
    if args.print:
        return
    elif args.automatic:
        reducer.automatic(args.max)
    elif args.segments:
        reducer.split_segments()
    elif args.reduce:
        reducer.reduce(args.max)
    else:
        reducer.split_files(args.max)
    print("Ready")

main()