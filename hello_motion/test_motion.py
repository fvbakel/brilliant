import unittest
from motion import *
from datetime import datetime

class TestDimensionScale(unittest.TestCase):

    def test_converts(self):
        dim_scale = DimensionScale((10,20),(100,100))
        self.assertEqual(dim_scale.result_dim,(100,50))
        self.assertEqual(dim_scale.scale_org_to_result,(10,2.5))

        point_1 = (20,5)
        point_1_org = dim_scale.res_to_org(point_1)
        self.assertEqual(point_1_org,(2,2))

class TestRectangle(unittest.TestCase):

    def test_rectangle_iterator(self):
        rectangle = Rectangle((2,2),(4,4))
        count = 0
        for index,pos in enumerate(rectangle):
            count += 1
            if index == 0:
                self.assertEqual(pos,(2,2))
            if index == 1:
                self.assertEqual(pos,(2,3))
            if index == 2:
                self.assertEqual(pos,(2,4))
            
            if index == 3:
                self.assertEqual(pos,(3,2))
            if index == 4:
                self.assertEqual(pos,(3,3))
            if index == 5:
                self.assertEqual(pos,(3,4))

            if index == 6:
                self.assertEqual(pos,(4,2))
            if index == 7:
                self.assertEqual(pos,(4,3))
            if index == 8:
                self.assertEqual(pos,(4,4))

        self.assertEqual(count,9)

    def test_size(self):
        rectangle = Rectangle((2,2),(4,4))
        self.assertEqual(rectangle.size_w_h,(3,3))

class TestPixToMeter(unittest.TestCase):

    def test_pix_to_meter(self):
        start_pos = (0,0)
        end_pos = (0,10)
        
        conv1 = PixToMeter(start_pos,end_pos,1)
        self.assertEqual(conv1.meter_per_pix,0.1)

        end_pos2 = (0,100)
        conv2 = PixToMeter(start_pos,end_pos2,1)
        self.assertEqual(conv2.meter_per_pix,0.01)

        self.assertEqual(conv2.get_dist_in_meter(start_pos,end_pos),0.1)

DATA_DIR = '/home/fvbakel/anna_data/falling_cone'
def make_one_frame_video():
    video = Video()
    video.nr_of_frames = 1
    video.fps = 1
    video.duration_sec = 0.0
    frame = cv2.imread(DATA_DIR + '/frame001.png')
    video.frames.append(frame)

    video.calculate_stats()
    return video

def make_few_frame_video():
    video = Video()
    frame = cv2.imread(DATA_DIR + '/sample_vid_0.png')
    video.frames.append(frame)
    frame = cv2.imread(DATA_DIR + '/sample_vid_50.png')
    video.frames.append(frame)
    frame = cv2.imread(DATA_DIR + '/sample_vid_55.png')
    video.frames.append(frame)
    frame = cv2.imread(DATA_DIR + '/sample_vid_60.png')
    video.frames.append(frame)
    video.fps = 4
    video.calculate_stats()
    return video
    

class TestTrackedObject(unittest.TestCase):

    def test_tracked_object(self):
        tracked_object = TrackedObject((10,10),5)
        tracked_object._init_traject(8)
        self.assertEqual(len(tracked_object.traject_w_h),8)

class TestVideo(unittest.TestCase):
    
    def test_video(self):
        video = make_one_frame_video()
        self.assertEqual(video.dim_h_w,(1920,1080))
        self.assertEqual(video.fps,1.0)
        self.assertEqual(video.nr_of_frames,1)
        self.assertAlmostEqual(video.duration_sec,0.0)
        self.assertEqual(len(video.frames),1)

        video = make_few_frame_video()
        self.assertEqual(video.dim_h_w,(1920,1080))
        self.assertEqual(video.fps,4.0)
        self.assertEqual(video.nr_of_frames,4)
        self.assertAlmostEqual(video.duration_sec,0.75)
        self.assertEqual(len(video.frames),4)

    def test_dump_video(self):
        # method below is for debug purpose only, disabled by default
        if False:
            video = Video.read_file(DATA_DIR + '/VID20221213162323.mp4')
            dump_video_to_img(video,'sample_vid')


class TestVideoAnalyses(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        TEST_TMP_DIR = "./tmp"
        logging.basicConfig(level=logging.DEBUG,filename=f"{TEST_TMP_DIR}/debug.log",filemode='w')

    def test_detect_tracked_object_at_pos(self):
        video = make_one_frame_video()
        analyses = MotionAnalyzes(video)
        tracked_object = analyses.detect_object_at_pos(frame_num=0,pos_inside_w_h=(636,326))

        self.assertEqual(tracked_object.start_pos_w_h,(636,326))
        
    def test_detect_tracked_object(self):
        video = make_few_frame_video()
        analyses = MotionAnalyzes(video)
        tracked_object = analyses.detect_object_at_pos(frame_num=0,pos_inside_w_h=(596,185))
        tracked_object._init_traject(4)
        analyses.add_tracked_object(tracked_object)
        logging.debug("Traject:")
        for pos in tracked_object.traject_w_h:
            logging.debug(pos)

        expected = (
                (591, 180),
                (586, 208),
                (587, 252),
                (589, 316)
        )
        tolerance = 5
        for index,pos in enumerate(tracked_object.traject_w_h):
            self.assertGreater(pos[0],expected[index][0] -tolerance,f"pos w > for {index}")
            self.assertLess(pos[0],expected[index][0] + tolerance,f"pos w < for {index}")
            self.assertGreater(pos[1],expected[index][1] -tolerance,f"pos h > for {index}")
            self.assertLess(pos[1],expected[index][1] + tolerance,f"pos h < for {index}")

    def _test_detect_tracked_object_bb(self):
        video = make_few_frame_video()
        analyses = MotionAnalyzes(video)
        tracked_object = TrackedObject((596,185),0)
        #tracked_object.bounding_box = Rectangle((550,157),(645,208))
        tracked_object.bounding_box = Rectangle((560,167),(635,198))
        tracked_object._init_traject(4)
        analyses.add_tracked_object(tracked_object)
        logging.debug("Traject:")
        for pos in tracked_object.traject_w_h:
            logging.debug(pos)

        expected = (
                (591, 180),
                (586, 208),
                (587, 252),
                (589, 316)
        )
        tolerance = 5
        for index,pos in enumerate(tracked_object.traject_w_h):
            self.assertGreater(pos[0],expected[index][0] -tolerance,f"pos w > for {index}")
            self.assertLess(pos[0],expected[index][0] + tolerance,f"pos w < for {index}")
            self.assertGreater(pos[1],expected[index][1] -tolerance,f"pos h > for {index}")
            self.assertLess(pos[1],expected[index][1] + tolerance,f"pos h < for {index}")

    def test_detect_tracked_object_sample(self):
        video = Video.read_file(DATA_DIR + '/VID20221213162323.mp4')
        analyses = MotionAnalyzes(video)
        #tracked_object = analyses.detect_object_at_pos(frame_num=0,pos_inside_w_h=(596,185))
        tracked_object = TrackedObject((596,185),0)
        #tracked_object.bounding_box = Rectangle((550,157),(645,208))
        #tracked_object.bounding_box = Rectangle((560,167),(635,198))
        #tracked_object.based_on_frame_index = 0
        tracked_object.bounding_box = Rectangle((555,296),(639,345))
        tracked_object.edge_size = 0
        tracked_object.based_on_frame_index = 60

        tracked_object._init_traject(4)
        analyses.add_tracked_object(tracked_object)
        logging.debug("Traject:")
        for pos in tracked_object.traject_w_h:
            logging.debug(pos)
    

if __name__ == "__main__":
    TEST_TMP_DIR = "./tmp"
    logging.basicConfig(level=logging.DEBUG,filename=f"{TEST_TMP_DIR}/debug.log",filemode='w')
    unittest.main()