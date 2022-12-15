import ffmpeg


def is_video(path):
    """
    Checks whether the file is a video file

    Argument(s):
        path: Absolute file path

    Returns:
        True/False depending on whether the file is a video file
    """
    try:
        if (
            ffmpeg.probe(path, select_streams="v")["streams"][0]["codec_type"]
            == "video"
        ):
            return True
        else:
            return False
    except:
        return False


def has_audio(path):
    """
    Checks whether the file contains audio stream(s)

    Argument(s):
        path: Absolute file path

    Returns:
        True/False depending on whether the file contains audio stream(s)
    """
    try:
        if (
            ffmpeg.probe(path, select_streams="a")["streams"][1]["codec_type"]
            == "audio"
        ):
            return True
        else:
            return False
    except:
        return False


def get_metadata(path):
    """
    Returns the metadata of a video file

    Argument(s):
        path: Absolute file path

    Returns:
        A tuple containing four entries:
            frame_rate: Framerate of video stream
            video_codec: Encoding format of video stream
            sample_rate: Sample rate of audio stream or "-" if no audio stream exists
            audio_codec: Encoding format of audio stream or "-" if no audio stream exists
        or an None if the file is not a video file
    """
    try:
        output = ["-", "-", "-", "-"]
        metadata = ffmpeg.probe(path)
        output[0] = str(round(eval(metadata["streams"][0]["avg_frame_rate"]), 2))
        output[1] = metadata["streams"][0]["codec_name"].upper()
        try:
            output[2] = metadata["streams"][1]["sample_rate"]
            output[3] = metadata["streams"][1]["codec_name"].upper()
        except:
            pass
        return tuple(output)
    except:
        return None


def transcode(
    input_file_path,
    output_file_path,
    frame_rate=25,
    video_codec="libx264",
    sample_rate=44100,
    audio_codec="aac",
):
    """
    Transcodes MP4 video file into specified audio/video encoding and framerate

    Argument(s):
        input_file_path: Absolute input file path
        output_file_path: Absolute output file path
        frame_rate: Target framerate of output video stream (Default: 25)
        video_codec: Target FFmpeg encoder of output video stream (Default: "libx264")
        sample_rate: Target sample rate of output audio stream (Default: 44100)
        audio_codec: Target FFmpeg encoder of output audio stream (Default: "aac")

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
