import ffmpeg


def is_video(path):
    """
    Checks whether the file is a video file

    Argument(s):
        path: Absolute file path

    Returns:
        True/False depending on whether the file is a video file
    """
    if ffmpeg.probe(path, select_streams="v")["streams"]:
        return True
    else:
        return False


def has_audio(path):
    """
    Checks whether the file contains audio stream(s)

    Argument(s):
        path: Absolute file path

    Returns:
        True/False depending on whether the file contains audio stream(s)
    """
    if ffmpeg.probe(path, select_streams="a")["streams"]:
        return True
    else:
        return False


def transcode(
    input_file_path,
    output_file_path,
    video_codec="libx264",
    frame_rate=25,
    audio_codec="aac",
    sample_rate=44100,
):
    """
    Transcodes MP4 video file into specified audio/video encoding and framerate

    Argument(s):
        input_file_path: Absolute input file path
        output_file_path: Absolute output file path
        video_codec: Target FFmpeg encoder of output video stream (Default: "libx264")
        frame_rate: Target framerate of output video stream (Default: 25)
        audio_codec: Target FFmpeg encoder of output audio stream (Default: "aac")
        sample_rate: Target sample rate of output audio stream (Default: 44100)

    Returns:
        Nothing
    """
    stream = ffmpeg.input(input_file_path)
    vid_stream = ffmpeg.filter(stream.video, "fps", fps=frame_rate)
    if has_audio(input_file_path):
        final_stream = ffmpeg.output(
            vid_stream,
            stream.audio,
            output_file_path,
            vcodec=video_codec,
            acodec=audio_codec,
            ar=sample_rate,
        )
    else:
        final_stream = ffmpeg.output(
            vid_stream,
            output_file_path,
            vcodec=video_codec,
        )
    ffmpeg.run(final_stream, quiet=True, overwrite_output=True)
