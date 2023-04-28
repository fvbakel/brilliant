import math
import argparse


class GpxReducer:

    def __init__(self,filename:str, max:int):
        self.filename=filename
        self.max=max
        self.outfilename = filename.replace(".gpx","") + "_reduced.gpx"

    def open_output(self):
        self.out = open(self.outfilename,"w")

    def reduce(self):
        
        start_str = "<trkpt" 
        count = 0

        # count lines
        with open(self.filename) as f:
            for line in f:
                if line.startswith(start_str):
                    count += 1

        to_reduce = count - self.max 
        print(f"Need to reduce from {count} to {self.max}")

        if to_reduce > 0 :
            remove_every = math.ceil(count / to_reduce )

            self.open_output()
            count =0
            with open(self.filename) as f:
                for line in f:
                    if line.startswith(start_str):
                        count += 1   
                        if (count % remove_every) != 0:
                            self.out.write(line)
                    else:
                        self.out.write(line)  

            self.out.close()


    


def main():
    parser = argparse.ArgumentParser(description="Reduce the number of points in a GPZ track")
    parser.add_argument('-m','--max', help='Max number of lines in outout', required=False,type=int,default=400)
    parser.add_argument('filename', help='Input filename', type=str)

    args = parser.parse_args()

    reducer = GpxReducer(args.filename,args.max)
    reducer.reduce()
    print("Ready")

main()