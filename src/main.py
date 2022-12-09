import os, video, defaults
from multiprocessing import Process


def setup_dirs(*dir_paths):
    """Create folder(s) if not existing
    Argument(s):
        *dir_paths: Absolute directory path(s)
    Returns:
        Nothing
    """
    for dir_path in [*dir_paths]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


def main():
    """Driver code"""
    setup_dirs(defaults.INPUT_DIR, defaults.OUTPUT_DIR)
    input_dir = (
        dir_path
        if os.path.exists(dir_path := input("Enter input folder: "))
        else defaults.OUTPUT_DIR
    )
    output_dir = (
        dir_path
        if os.path.exists(dir_path := input("Enter output folder: "))
        else defaults.OUTPUT_DIR
    )
    for input_file in os.listdir(input_dir):
        input_file_path = os.path.join(input_dir, input_file)
        if video.is_video(input_file_path):
            print(f"Converting {input_file}")
            setup_dirs(
                os.path.join(output_dir, "H264"), os.path.join(output_dir, "H265")
            )
            output_file_path_h264 = os.path.join(output_dir, "H264", input_file)
            output_file_path_h265 = os.path.join(output_dir, "H265", input_file)
            h264_transcode = Process(
                target=video.transcode,
                args=(input_file_path, output_file_path_h264, 25, "libx264", "aac"),
            )
            h265_transcode = Process(
                target=video.transcode,
                args=(input_file_path, output_file_path_h265, 25, "libx265", "aac"),
            )
            h264_transcode.start()
            h265_transcode.start()
            h264_transcode.join()
            h265_transcode.join()
        else:
            print(f"{input_file} is not a video file, skipping")
        break


if __name__ == "__main__":
    main()
