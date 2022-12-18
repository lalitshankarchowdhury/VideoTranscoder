import ffmpeg


def get_metadata(path):
    """
    Returns the metadata of a video file

    Argument(s):

        path: Absolute file path

    Returns:

        A dictionary containing four keys:

            video_codec: Encoding format of video stream or "-" if no video stream exists

            frame_rate: Framerate of video stream or "-" if no video stream exists

            audio_codec: Encoding format of audio stream or "-" if no audio stream exists

            sample_rate: Sample rate of audio stream or "-" if no audio stream exists
    """
    output = {
        "video_codec": "-",
        "frame_rate": "-",
        "audio_codec": "-",
        "sample_rate": "-",
    }
    try:
        av_metadata = ffmpeg.probe(path)["streams"]
        video_metadata = [x for x in av_metadata if x["codec_type"] == "video"]
        audio_metadata = [x for x in av_metadata if x["codec_type"] == "audio"]
        output["video_codec"] = video_metadata[0]["codec_name"].upper()
        output["frame_rate"] = str(round(eval(video_metadata[0]["r_frame_rate"]), 2))
        try:
            output["audio_codec"] = audio_metadata[0]["codec_name"].upper()
            output["sample_rate"] = audio_metadata[0]["sample_rate"]
        except:
            pass
    except:
        pass
    return output


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

        input_file_path: Absolute path of input file

        output_file_path: Absolute path of output file

        video_codec: Encoding format of video stream or "-" if no video stream exists

        frame_rate: Framerate of video stream or "-" if no video stream exists

        audio_codec: Encoding format of audio stream or "-" if no audio stream exists

        sample_rate: Sample rate of audio stream or "-" if no audio stream exists

    Returns:

        None
    """
    stream = ffmpeg.input(input_file_path)
    vid_stream = ffmpeg.filter(stream.video, "fps", fps=frame_rate)
    if get_metadata(input_file_path)["audio_codec"] != "-":
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
