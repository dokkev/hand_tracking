########################################################################
#
# Copyright (c) 2022, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################

"""
    Read SVO sample to read the video and the information of the camera. It can pick a frame of the svo and save it as
    a JPEG or PNG file. Depth map and Point Cloud can also be saved into files.
"""
import sys
import pyzed.sl as sl
import cv2
import numpy as np


def main():

    if len(sys.argv) != 2:
        print("Please specify path to .svo file.")
        exit()

    filepath = sys.argv[1]
    print("Reading SVO file: {0}".format(filepath))

    input_type = sl.InputType()
    input_type.set_from_svo_file(filepath)
    init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
    init.depth_mode = sl.DEPTH_MODE.QUALITY

    cam = sl.Camera()
    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    runtime = sl.RuntimeParameters()
    runtime.sensing_mode = sl.SENSING_MODE.FILL 
    mat = sl.Mat()
    depth = sl.Mat()
    pcl = sl.Mat()
    frame = 0
    key = ''
    end = False

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter('test.mp4',fourcc, 20.0, (cam.get_camera_information().camera_resolution.width,cam.get_camera_information().camera_resolution.height))

    print("  Save the current image:     s")
    print("  Quit the video reading:     q\n")
    while end is False:  # for 'q' key
        frame += 1
        print("Current Frame: ({:1})".format(frame), end="\r")
        final_frame = cam.get_svo_number_of_frames()
        if frame == final_frame:
            end=True
            
        err = cam.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            cam.retrieve_image(mat)
            cam.retrieve_image(depth, sl.VIEW.DEPTH)
            cam.retrieve_measure(pcl, sl.MEASURE.XYZRGBA)
            img = mat.get_data()
            cv2.putText(img,str(int(frame)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
            cv2.imshow("ZED", img)
            key = cv2.waitKey(1)
            out.write(img)
            saving_image(key, mat)

        else:
            key = cv2.waitKey(1)
    cv2.destroyAllWindows()

    print_camera_information(cam)
    cam.close()
    out.release()
    print("\nFINISH")


def print_camera_information(cam):
    while True:
        res = input("Do you want to display camera information? [y/n]: ")
        if res == "y":
            print()
            print("Distorsion factor of the right cam before calibration: {0}.".format(
                cam.get_camera_information().calibration_parameters_raw.right_cam.disto))
            print("Distorsion factor of the right cam after calibration: {0}.\n".format(
                cam.get_camera_information().calibration_parameters.right_cam.disto))

            print("Confidence threshold: {0}".format(cam.get_runtime_parameters().confidence_threshold))
            print("Depth min and max range values: {0}, {1}".format(cam.get_init_parameters().depth_minimum_distance,
                                                                    cam.get_init_parameters().depth_maximum_distance)
)
            print("Resolution: {0}, {1}.".format(round(cam.get_camera_information().camera_resolution.width, 2), cam.get_camera_information().camera_resolution.height))
            print("Camera FPS: {0}".format(cam.get_camera_information().camera_fps))
            print("Frame count: {0}.\n".format(cam.get_svo_number_of_frames()))
            break
        elif res == "n":
            print("Camera information not displayed.\n")
            break
        else:
            print("Error, please enter [y/n].\n")


def saving_image(key, mat):
    if key == 115:
        img = sl.ERROR_CODE.FAILURE
        while img != sl.ERROR_CODE.SUCCESS:
            filepath = input("Enter filepath name: ")
            img = mat.write(filepath)
            print("Saving image : {0}".format(repr(img)))
            if img == sl.ERROR_CODE.SUCCESS:
                break
            else:
                print("Help: you must enter the filepath + filename + PNG extension.")



if __name__ == "__main__":
    main()
