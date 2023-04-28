import numpy as np
import cv2
from datetime import datetime
import logging
import math
from enum import Enum

DATA_DIR = '/home/fvbakel/anna_data/falling_cone'

def dump_frame(frame, name:str=None):
    if frame is not None:
        if name is None:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            name = "frame_" +timestamp
        cv2.imwrite(DATA_DIR + "/"+ name + ".png", frame)

def dump_video_to_img(video,base_name:str=None):
    if base_name is None:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        base_name = "frame_" +timestamp

    for index,frame in enumerate(video.frames):
        dump_frame(frame,f"{base_name}_{index}")

class Configuration:

    def __init__(self):
        self.data_dir = DATA_DIR
        
        self.max_width = 600
        self.max_height = 600
        self.max_dim = (self.max_height,self.max_width)

class Rectangle:

    def __init__(self,up_left:tuple[int,int],down_right:tuple[int,int]):
        self.up_left=up_left
        self.down_right=down_right

    @property
    def size_w_h(self):
        w = (self.down_right[0] - self.up_left[0]) + 1
        h = (self.down_right[1] - self.up_left[1]) + 1
        return (w,h)

    def __iter__(self):
        return RectangleIterator(self)

class RectangleIterator:

    def __init__(self,rectangle:Rectangle):
        self.rectangle = rectangle
        self.idx = 0
        self.positions:list[tuple[int,int]] = []
        self._init_positions()
    
    def _init_positions(self):
        for w in range(self.rectangle.up_left[0],self.rectangle.down_right[0] + 1):
            for h in range(self.rectangle.up_left[1],self.rectangle.down_right[1] +1):
                self.positions.append((w,h))

    def __iter__(self):
        return self

    def __next__(self):
        self.idx += 1
        try:
            return self.positions[self.idx-1]
        except IndexError:
            self.idx = 0
            raise StopIteration 

class PixToMeter:

    def __init__(self,start_pos_h_w:tuple[int,int],end_pos_h_w:tuple[int,int],size_meter:float):
        self.start_pos_h_w = start_pos_h_w
        self.end_pos_h_w = end_pos_h_w
        self.size_meter = size_meter
        self._calc_conversion()

    def _calc_conversion(self):
        pix_dist = PixToMeter.calc_distance(self.start_pos_h_w,self.end_pos_h_w)
        self.meter_per_pix = float(self.size_meter) / pix_dist
    
    def get_dist_in_meter(self,start_pos_h_w:tuple[int,int],end_pos_h_w:tuple[int,int]):
        pix_dist = PixToMeter.calc_distance(start_pos_h_w,end_pos_h_w)
        return pix_dist * self.meter_per_pix

    def calc_distance(start_pos_h_w:tuple[int,int],end_pos_h_w:tuple[int,int]):
        delta_h = start_pos_h_w[0] - end_pos_h_w[0]
        delta_w = start_pos_h_w[1] - end_pos_h_w[1]
        return  math.sqrt((delta_h**2) + (delta_w**2))

class TrackedObject:

    def __init__(self,start_pos_w_h:tuple[int,int],based_on_frame_index:int):
        self.name:str = None
        self.start_pos_w_h = start_pos_w_h
        self.based_on_frame_index = based_on_frame_index
        self.start_color:int = 0
        self.min_color:int = 0
        self.max_color:int = 0
        self.bounding_box = Rectangle(start_pos_w_h,start_pos_w_h)
        self.traject_w_h:list[tuple[int,int]] = []
        self.edge_size = 2
    
    def _init_traject(self,nr_of_frames:int ):
        self.traject_w_h = [self.bounding_box.up_left] * nr_of_frames

class Video:

    def __init__(self):
        self.nr_of_frames:int = 0
        self.fps:float = 0
        self.duration_sec:float = 0.0
        self.frames = []
        self.dim_h_w = (0,0)

    def calculate_stats(self):
        self.nr_of_frames = len(self.frames)
        if self.nr_of_frames > 0:
            self.duration_sec = self.index_to_timestamp(self.nr_of_frames -1)
            self.dim_h_w = self.frames[0].shape[:2]

    def index_to_timestamp(self,frame_index:int) -> float:
        if self.fps == 0:
            return 0.0
        else:
            return frame_index / self.fps

    def _copy_stats(self):
        clone  = Video()
        clone.fps = self.fps
        clone.duration_sec = self.duration_sec
        clone.nr_of_frames = self.nr_of_frames
        clone.dim_h_w = self.dim_h_w
        return clone

    def generate_grey(self):
        grey_video:Video = self._copy_stats()
        for frame in self.frames:
            grey_video.frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

        return grey_video

    def read_file(filename:str):
        video = Video()

        cap = cv2.VideoCapture(filename)
        video.fps = Video.get_fps(cap)
        while True:
            if  cap is not None and cap.isOpened():
                ret, frame = cap.read()
            if not ret:
                break
            video.frames.append(frame)
        video.calculate_stats()
        return video
    
    def get_fps(cap) -> float:
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    
        if int(major_ver)  < 3 :
            return cap.get(cv2.cv.CV_CAP_PROP_FPS)
        else :
            return cap.get(cv2.CAP_PROP_FPS)
    


class MotionAnalyzes:
    def __init__(self,video:Video):
        self._tracked_objects:list[TrackedObject] = []
        self.video = video
        self.grey_video = self.video.generate_grey()
    
    def add_tracked_object(self,tracked_object:TrackedObject):
        self.calculate_traject(tracked_object)
        self._tracked_objects.append(tracked_object)
    
    def get_sub_img(img,offset:tuple[int,int],rectangle:Rectangle):
        w,h = offset
        return img[h:h + rectangle.size_w_h[1],w + rectangle.size_w_h[0]]
        
    def set_search_img_tracked_object(self,tracked_object:TrackedObject):
        edge_size = tracked_object.edge_size
        search_frame = self.video.frames[tracked_object.based_on_frame_index]
        w,h = tracked_object.bounding_box.up_left
        w_min = w - edge_size
        w_max = w + tracked_object.bounding_box.size_w_h[0] + edge_size

        h_min = h - edge_size
        h_max = h + tracked_object.bounding_box.size_w_h[1] + edge_size

        h_size = self.video.dim_h_w[0]
        w_size = self.video.dim_h_w[1]

        if w_min < 0:
            w_min = 0
        if h_min < 0:
            h_min = 0

        if w_max > w_size:
            w_max = w_size
        if h_max > h_size:
            h_max = h_size

        #result = cv2.bitwise_and(search_frame,self.empty, mask = self.motion_mask)
        self.img_to_search = search_frame[
            h_min:h_max,
            w_min:w_max
        ]

    def make_color_filter(self,img,nr_of_clusters=2):
        Z = img.reshape((-1,3))

        # convert to np.float32
        Z = np.float32(Z)

        # define criteria, number of clusters(K) and apply kmeans()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret,label,center=cv2.kmeans(Z,nr_of_clusters,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

        # Now convert back into uint8, and make original image
        center = np.uint8(center)
        res = center[label.flatten()]
        res2 = res.reshape((img.shape))
        return res2

    def detect_object_at_pos(self,frame_num:int,pos_inside_w_h:tuple[int,int],threshold = 20):
        tracked_object = TrackedObject(pos_inside_w_h,frame_num)
        start_w= pos_inside_w_h[0]
        start_h= pos_inside_w_h[1]
        frame_grey = self.grey_video.frames[frame_num]
        tracked_object.start_color = frame_grey[start_h,start_w]
        logging.debug(f"start_color={tracked_object.start_color}")
        tracked_object.min_color = tracked_object.start_color - threshold
        tracked_object.max_color = tracked_object.start_color + threshold
        min_w = pos_inside_w_h[0]
        min_h = pos_inside_w_h[1]
        max_w = pos_inside_w_h[0]
        max_h = pos_inside_w_h[1]

        while True:
            cur_color = frame_grey[(start_h,min_w)]
            logging.debug(f"min_w = {min_w}  cur_color={cur_color}")
            if cur_color < tracked_object.min_color or cur_color > tracked_object.max_color: 
                break
            if min_w == 0:
                break
            min_w -= 1
        
        while True:
            cur_color = frame_grey[(min_h,start_w)]
            if cur_color < tracked_object.min_color or cur_color > tracked_object.max_color:
                logging.debug(f"min_w = {min_h}  cur_color={cur_color}")
                break
            if min_h == 0:
                break
            min_h -= 1

        while True:
            cur_color = frame_grey[(start_h,max_w)]
            logging.debug(f"max_w = {max_w}  cur_color={cur_color}")
            if cur_color < tracked_object.min_color or cur_color > tracked_object.max_color:
                break
            if max_w == self.video.dim_h_w[1]-1:
                break
            max_w += 1
        
        while True:
            cur_color = frame_grey[(max_h,start_w)]
            if cur_color < tracked_object.min_color or cur_color > tracked_object.max_color:
                logging.debug(f"max_h = {max_h}  cur_color={cur_color}")
                break
            if max_h == self.video.dim_h_w[0]-1:
                break
            max_h += 1

        tracked_object.bounding_box.up_left = (min_w, min_h)
        tracked_object.bounding_box.down_right = (max_w, max_h)


        tmp_img = cv2.rectangle(
            self.video.frames[frame_num],
            #frame_grey,
            tracked_object.bounding_box.up_left,
            tracked_object.bounding_box.down_right,
            255,
            1
        )

        dump_frame(tmp_img,name="debug_img")
        return tracked_object

    def _detect_object_in_frame_w_h(self,tracked_object:TrackedObject,frame_index:int) ->tuple[int,int]:
        #img_to_search = self.get_search_img_tracked_object(tracked_object)
        # TODO make configurable from outside
        methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

        method = eval(methods[1])
        result = cv2.bitwise_and(self.video.frames[frame_index],self.empty, mask = self.motion_mask)
        # Apply template Matching
        res = cv2.matchTemplate(
            #self.video.frames[frame_index],
            result,
            self.img_to_search,
            method
        )
        if frame_index == 1:
            dump_frame(self.img_to_search,name=f"search_img_{frame_index}")
            dump_frame(result,name=f"masked_img_{frame_index}")
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left_w_h = min_loc
        else:
            top_left_w_h = max_loc

        return top_left_w_h

    def make_motion_mask(self,threshold = 55):
        motion_mask = np.zeros(self.video.frames[0].shape[:2],dtype=np.uint8) 
        for cur_frame_idx in range(1,self.video.nr_of_frames):
            diff_img_gray = cv2.subtract(
                self.grey_video.frames[cur_frame_idx-1],
                self.grey_video.frames[cur_frame_idx]
            )
            #dump_frame(diff_img_gray,name=f"diff_img_gray_{cur_frame_idx}")
            #(thresh, mask) = cv2.threshold(self.grey_video.frames[cur_frame_idx], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            #diff_img_gray = cv2.cvtColor(diff_img,cv2.COLOR_BGR2GRAY)
            #dump_frame(diff_img_gray,name=f"diff_img_gray{cur_frame_idx}")
            (thresh, mask) = cv2.threshold(diff_img_gray, threshold, 255, cv2.THRESH_BINARY)
            motion_mask = motion_mask + mask
            #dump_frame(mask,name=f"mask_{cur_frame_idx}")
            #dump_frame(motion_mask,name=f"motion_mask_{cur_frame_idx}")
        return motion_mask

    def calculate_traject(self,tracked_object:TrackedObject):
        tracked_object._init_traject(self.video.nr_of_frames)
        self.empty = np.ones_like(self.video.frames[0]) * 255
        self.motion_mask = self.make_motion_mask(5)
        self.set_search_img_tracked_object(tracked_object)
        img_to_search_filter = self.make_color_filter(self.img_to_search,3)
        dump_frame(img_to_search_filter,name=f"img_to_search_filter")
        dump_frame(self.motion_mask,name=f"motion_mask")
        for cur_frame_idx in range(0,self.video.nr_of_frames):
            top_left_w_h:tuple[int,int] = tracked_object.bounding_box.up_left
            if cur_frame_idx != tracked_object.based_on_frame_index:
                top_left_w_h = self._detect_object_in_frame_w_h(tracked_object,cur_frame_idx)
            else:
                top_left_w_h:tuple[int,int] = tracked_object.bounding_box.up_left
            tracked_object.traject_w_h[cur_frame_idx] = top_left_w_h

            # Below is for debug
            if cur_frame_idx < 5 or (cur_frame_idx % 5 == 0):
                tmp_img = self.draw_bounding_box(tracked_object,cur_frame_idx)
                dump_frame(tmp_img,name=f"detect_img_{cur_frame_idx}")
                #filter_img = self.make_color_filter(self.video.frames[cur_frame_idx],3)
                #dump_frame(filter_img,name=f"filter_img{cur_frame_idx}")
                if False and cur_frame_idx > 1:
                    diff_img = cv2.subtract(
                        self.video.frames[cur_frame_idx-1],
                        self.video.frames[cur_frame_idx]
                    )
                    #(thresh, mask) = cv2.threshold(self.grey_video.frames[cur_frame_idx], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    diff_img_gray = cv2.cvtColor(diff_img,cv2.COLOR_BGR2GRAY)
                    (thresh, mask) = cv2.threshold(diff_img_gray, 55, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                    
                    #np.putmask(result,diff_img > 0,self.video.frames[cur_frame_idx])
                    result = cv2.bitwise_and(self.video.frames[cur_frame_idx],empty, mask = self.motion_mask)
                    #dump_frame(diff_img_gray,name=f"diff_img_gray{cur_frame_idx}")
                    #dump_frame(mask,name=f"mask_img_{cur_frame_idx}")
                    dump_frame(empty,name=f"empty_img_{cur_frame_idx}")
                    dump_frame(result,name=f"result_img_{cur_frame_idx}")
        
    def draw_bounding_box(self,tracked_object:TrackedObject,frame_index:int):
        w_start,h_start = tracked_object.traject_w_h[frame_index]

        # TODO: correct this in the traject!
        if frame_index != tracked_object.based_on_frame_index:
            w_start += tracked_object.edge_size
            h_start += tracked_object.edge_size
        
        w_size,h_size = tracked_object.bounding_box.size_w_h
        pos_left_up=(w_start,h_start)
        pos_right_down = (w_start+w_size,h_start+h_size)
        base_img =  np.copy(self.video.frames[frame_index])
        tmp_img = cv2.rectangle(
            base_img,
            pos_left_up,
            pos_right_down,
            255,
            1
        )
        return tmp_img

    def _notused_detect_object_in_frame(self,tracked_index:int,frame_index:int):
        tracked_obj = self._tracked_objects[tracked_index]
        previous_frame_index:int
        if tracked_obj.based_on_frame_index == frame_index:
            return tracked_obj
        elif tracked_obj.based_on_frame_index > frame_index:
            previous_frame_index = frame_index + 1
        else:
            previous_frame_index = frame_index - 1

        start_w = tracked_obj.traject_w_h[previous_frame_index][0]
        start_h = tracked_obj.traject_w_h[previous_frame_index][1]

        
class DimensionScale:

    def __init__(self,org_dim:tuple[int,int],max_dim:tuple[int,int]):
        self.org_dim = org_dim
        self.max_dim = max_dim
        self.result_dim: tuple(int,int) = None
        self.scale_org_to_result: tuple(float,float) = None
        self.init_derived()

    def init_derived(self):
        h, w = self.org_dim
        h_max,w_max = self.max_dim
        rw = w_max / float(w)
        rh = h_max / float(h)
        
        h_for_w= int(h * rw)
        w_for_h= int(w * rh)
        
        if h_for_w > h_max:
            self.result_dim= (w_for_h, h_max)
        else:
            self.result_dim= (w_max, h_for_w)

        h_res, w_res = self.result_dim
        self.scale_org_to_result = ( h_res/float(h), w_res/float(w))

    def org_to_res(self,location:tuple[int,int]):
        h, w = location
        h_scale, w_scale = self.scale_org_to_result
        h_res = int(h*h_scale)
        w_res = int(w*w_scale)
        return (h_res,w_res)
    
    def res_to_org(self,location:tuple[int,int]):
        h, w = location
        h_scale, w_scale = self.scale_org_to_result
        h_res = int(h/h_scale)
        w_res = int(w/w_scale)
        return (h_res,w_res)

class VideoView:

    def __init__( self,
                org_video:Video,
                dim_scale:DimensionScale):
        self.org_video = org_video
        self.result_video = Video()
        self.dim_scale = dim_scale
        self.current_frame_index = 0
        self._make_result()

    def _make_result(self):
        pass

    def get_current_frame(self):
        return self.result_video.frames[self.current_frame_index]



