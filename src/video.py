import ffmpeg


def get_metadata(path):
    """
    Returns the metadata of a video file

    Argument(s):
        path: Absolute file path

    Returns:
        A dictionary containing four keys:
            frame_rate: Framerate of video stream or "-" if no video stream exists
            video_codec: Encoding format of video stream or "-" if no video stream exists
            sample_rate: Sample rate of audio stream or "-" if no audio stream exists
            audio_codec: Encoding format of audio stream or "-" if no audio stream exists
    """
    output = {
        "frame_rate": "-",
        "video_codec": "-",
        "sample_rate": "-",
        "audio_codec": "-",
    }
    try:
        video_metadata = ffmpeg.probe(path, select_streams="v")
        output["frame_rate"] = str(
            round(eval(video_metadata["streams"][0]["r_frame_rate"]), 2)
        )
        output["video_codec"] = video_metadata["streams"][0]["codec_name"].upper()
        try:
            audio_metadata = ffmpeg.probe(path, select_streams="a")
            output["sample_rate"] = audio_metadata["streams"][0]["sample_rate"]
            output["audio_codec"] = audio_metadata["streams"][0]["codec_name"].upper()
        except:
            pass
    except:
        pass
    return output


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
        input_file_path: Absolute path of input file
        output_file_path: Absolute path of output file
        frame_rate: Target framerate of output video stream (Default: 25)
        video_codec: Target FFmpeg encoder of output video stream (Default: "libx264")
        sample_rate: Target sample rate of output audio stream (Default: 44100)
        audio_codec: Target FFmpeg encoder of output audio stream (Default: "aac")

    Returns:
        Nothing
    """
    stream = ffmpeg.input(input_file_path)
    vid_stream = ffmpeg.filter(stream.video, "fps", fps=frame_rate)
    if get_metadata(input_file_path)["audio_codec"] != "-":
        print(f"{input_file_path} contains audio")
        final_stream = ffmpeg.output(
            vid_stream,
            stream.audio,
            output_file_path,
            vcodec=video_codec,
            acodec=audio_codec,
            ar=sample_rate,
        )
    else:
        print(f"{input_file_path} contains no audio")
        final_stream = ffmpeg.output(
            vid_stream,
            output_file_path,
            vcodec=video_codec,
        )
    ffmpeg.run(final_stream, quiet=True, overwrite_output=True)
