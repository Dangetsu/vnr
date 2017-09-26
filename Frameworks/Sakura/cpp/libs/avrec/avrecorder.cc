// avrecorder.cc
// 9/20/2014 jichi

#include "avrec/avrecorder.h"
#include "avrec/avsettings.h"
extern "C" {
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavutil/imgutils.h>
#include <libswscale/swscale.h>
} // extern "C"
#include <string>

#define SK_NO_QT
#define DEBUG "avrecorder.cc"
#include "sakurakit/skdebug.h"

/** Private class */


class AVRecorderPrivate
{
public:
  std::string path;
  AVRecorderSettings settings;
  int64_t frameCount;

  // constant
  AVFormatContext *formatContext;
  AVStream *videoStream;
  AVCodecContext *videoCodecContext;
  AVCodec *videoCodec;
  AVBufferRef *videoBuffer;
  size_t videoBufferSize;
  AVBufferRef *pictureBuffer;
  size_t pictureBufferSize;
  AVFrame *videoPicture;
  SwsContext *imageConvertContext;

  AVRecorderPrivate()
    : frameCount(0)
  {}
};

/** Public class */

AVRecorder::AVRecorder() : d_(new D) {}
AVRecorder::~AVRecorder() { delete d_; }

// Properties

AVRecorderSettings *AVRecorder::settings() const { return &d_->settings; }

const char *AVRecorder::path() const { return d_->path.c_str(); }
void AVRecorder::setPath(const char *path) { d_->path = path; }

// Prepare

bool AVRecorder::init()
{
  avcodec_register_all();
  av_register_all();
  return true;
}

bool AVRecorder::start()
{
  DOUT("enter");
  // Init ffmpeg stuff

  // Format
  AVOutputFormat *outputFormat = av_guess_format(NULL, d_->path.c_str(), NULL);
  if (!outputFormat) {
    DOUT("leave: unable to get an output format by passed filename");
    return false;
  }

  d_->formatContext = avformat_alloc_context();
  d_->formatContext->oformat = outputFormat;

  // http://stackoverflow.com/questions/19146587/how-do-you-enable-veryfast-libx264-preset-from-code-using-libavcodec
  //av_opt_set(m_formatContext->priv_data, "preset", "veryfast", 0);

  // Create video
  //AVStream *m_videoStream = av_new_stream(m_formatContext,0);
  d_->videoStream = avformat_new_stream(d_->formatContext, nullptr);
  if (!d_->videoStream) {
    //q_ptr->setError(Encoder::InvalidVideoStreamError, tr("Unable to add video stream."));
    DOUT("leave: unable to add video stream");
    return false;
  }

  // Set up video codec
  d_->videoCodecContext = d_->videoStream->codec;

  //d_->videoCodecContext->codec_id = (videoCodec() == EncoderGlobal::DEFAULT_VIDEO_CODEC) ? d_->outputFormat->video_codec : static_cast<CodecID>(videoCodec());
  //d_->videoCodecContext->codec_id = d_->outputFormat->video_codec;
  //qDebug() << "video codec id" << d_->videoCodecContext->codec_id;
  d_->videoCodecContext->codec_id =  AV_CODEC_ID_H264;

  d_->videoCodecContext->codec_type = AVMEDIA_TYPE_VIDEO;

  //d_->videoCodecContext->width = videoSize().width();
  //d_->videoCodecContext->height = videoSize().height();
  //d_->videoCodecContext->width = 1280;
  //d_->videoCodecContext->height = 720;

  d_->videoCodecContext->width = d_->settings.width;
  d_->videoCodecContext->height = d_->settings.height;

  //d_->videoCodecContext->pix_fmt = (PixelFormat)outputPixelFormat();
  d_->videoCodecContext->pix_fmt = AV_PIX_FMT_YUV420P;
  //d_->videoCodecContext->time_base.den = fixedFrameRate() != -1 ? fixedFrameRate() : 1000;
  //d_->videoStream->time_base.den = 1000 / videoTimer_->interval();
  d_->videoStream->time_base.den = d_->settings.fps;
  d_->videoStream->time_base.num = 1;

  //applyVideoCodecSettings();
  // http://stackoverflow.com/questions/3553003/encoding-h-264-with-libavcodec-x264
  //auto ctx = d_->videoCodecContext;
  //ctx->bit_rate = 5000 * 1000;
  //ctx->bit_rate_tolerance = 0;
  //ctx->rc_max_rate = 0;
  //ctx->rc_buffer_size = 0;
  //ctx->gop_size = 40;
  //ctx->max_b_frames = 3;
  //ctx->b_frame_strategy = 1;
  //ctx->coder_type = 1;
  //ctx->me_cmp = 1;
  //ctx->me_range = 16;
  //ctx->qmin = 10;
  //ctx->qmax = 51;
  //ctx->scenechange_threshold = 40;
  //ctx->flags |= CODEC_FLAG_LOOP_FILTER;
  //ctx->me_method = ME_HEX;
  //ctx->me_subpel_quality = 5;
  //ctx->i_quant_factor = 0.71;
  //ctx->qcompress = 0.6;
  //ctx->max_qdiff = 4;
  //ctx->directpred = 1;
  //ctx->flags2 |= CODEC_FLAG2_FASTPSKIP;


  // http://stackoverflow.com/questions/15914012/encoding-a-screenshot-into-a-video-using-ffmpeg
  auto c = d_->videoCodecContext;
  //c->bit_rate = 400* 000;
  //c->bit_rate = 500* 000;
  c->bit_rate = 1000 * 000;
  c->width = d_->settings.width;                    // resolution must be a multiple of two (1280x720),(1900x1080),(720x480)
  c->height = d_->settings.height;
  c->time_base.num = 1;                   // framerate numerator
  c->time_base.den = d_->settings.fps;                 // framerate denominator
  // http://forum.videohelp.com/threads/249602-How-does-GOP-size-affect-recording
  // https://en.wikipedia.org/wiki/MPEG-2
  //  For PAL the maximum length of a GOP is 15 frames, for NTSC is it 18. Longer GOPs can provide better compression.
  //c->gop_size = 10;                     // emit one intra frame every ten frames
  //c->gop_size = 18; // use NTSC standard, 30fps = 0.625 second
  //c->gop_size = 15; // use PAL standard, 25fps, 0.6 second = 1/25*15, a wrong value would result in non monotonic DTS warning
  c->gop_size = d_->settings.gop;

  c->max_b_frames = 1;                  // maximum number of b-frames between non b-frames
  c->keyint_min = 1;                    // minimum GOP size
  c->i_quant_factor = 0.71;            // qscale factor between P and I frames
  c->b_frame_strategy = 20;                 ///// find out exactly what this does
  c->qcompress = 0.6;                ///// find out exactly what this does
  c->qmin = 20;                       // minimum quantizer
  c->qmax = 51;                       // maximum quantizer
  c->max_qdiff = 4;                     // maximum quantizer difference between frames
  c->refs = 4;                      // number of reference frames
  c->trellis = 1;                     // trellis RD Quantization
  c->pix_fmt = AV_PIX_FMT_YUV420P;               // universal pixel format for video encoding
  c->codec_id = AV_CODEC_ID_H264;
  c->codec_type = AVMEDIA_TYPE_VIDEO;

  // Open video stream
  d_->videoCodec = avcodec_find_encoder(d_->videoCodecContext->codec_id);
  if (!d_->videoCodec) {
    //q_ptr->setError(Encoder::VideoEncoderNotFoundError, tr("Unable to find video encoder by codec id."));
    DOUT("leave: unable to find video encoder by codec id");
    return false;
  }

  // open the codec
  // http://stackoverflow.com/questions/19146587/how-do-you-enable-veryfast-libx264-preset-from-code-using-libavcodec
  //AVDictionary *codec_options = nullptr;
  //av_dict_set(&codec_options, "preset", "medium", 0);
  //av_dict_set( &codec_options, "AnyCodecParameter", "Value", 0);
  //if (avcodec_open2(d_->videoCodecContext, d_->videoCodec, &codec_options) < 0) {
  if (avcodec_open2(d_->videoCodecContext, d_->videoCodec, nullptr) < 0) {
    //q_ptr->setError(Encoder::InvalidVideoCodecError, tr("Unable to open video codec."));
    DOUT("leave: unable to open video codec");
    return false;
  }

  //allocate frame buffer
  //int d_->videoBufferSize = videoSize().width() * videoSize().height() * 1.5;
  d_->videoBufferSize = d_->videoCodecContext->width * d_->videoCodecContext->height * 1.5;
  //AVBuffer *d_->videoBuffer = new AVBuffer[d_->videoBufferSize];
  d_->videoBuffer = av_buffer_alloc(d_->videoBufferSize);

  //init frame
  d_->videoPicture = avcodec_alloc_frame();

  d_->pictureBufferSize = avpicture_get_size(d_->videoCodecContext->pix_fmt, d_->videoCodecContext->width, d_->videoCodecContext->height);
  d_->pictureBuffer = av_buffer_alloc(d_->pictureBufferSize);

  // Setup the planes
  avpicture_fill((AVPicture *)d_->videoPicture, d_->pictureBuffer->data, d_->videoCodecContext->pix_fmt, d_->videoCodecContext->width, d_->videoCodecContext->height);

  if (avio_open(&d_->formatContext->pb, d_->path.c_str(), AVIO_FLAG_WRITE) < 0) {
    //q_ptr->setError(Encoder::FileOpenError, QString(tr("Unable to open: %1")).arg(filePath()));
    DOUT("leave: unable to open:" << d_->path);
    return false;
  }

  // Finalize format

  // See: ffmpeg/doc/examples/muxing.c
  if (d_->formatContext->oformat->flags & AVFMT_GLOBALHEADER)
      d_->videoCodecContext->flags |= CODEC_FLAG_GLOBAL_HEADER;
  avformat_write_header(d_->formatContext, 0);

  DOUT("leave: success");
  return true;
}

// Finalize

bool AVRecorder::stop()
{
  DOUT("enter");
  av_write_trailer(d_->formatContext);
  avcodec_close(d_->videoCodecContext);
  av_free(d_->videoCodecContext);
  av_free(d_->videoStream);
  sws_freeContext(d_->imageConvertContext);
  avio_close(d_->formatContext->pb);
  DOUT("leave");
  return true;
}

// Video

bool AVRecorder::addImageData(const uint8_t *data, int64_t size, int bytesPerLine, int width, int height, AVPixelFormat fmt)
{
  DOUT("enter");
  if (fmt == AV_PIX_FMT_NONE) {
    DOUT("leave: invalid image format");
    return false;
  }

  d_->imageConvertContext = sws_getCachedContext(d_->imageConvertContext, width, height, fmt,
                                                 d_->videoCodecContext->width, d_->videoCodecContext->height, d_->videoCodecContext->pix_fmt,
                                                 SWS_BICUBIC, NULL, NULL, NULL);
  if (!d_->imageConvertContext) {
    DOUT("leave: unable to initialize conversion context");
    return false;
  }

   const uint8_t *srcplanes[3] = { data, 0, 0 };
   int srcstride[3] = { bytesPerLine, 0, 0 };
   sws_scale(d_->imageConvertContext, srcplanes, srcstride, 0, height, d_->videoPicture->data, d_->videoPicture->linesize);

   //pkt.pts = m_videoCodecContext->coded_frame->pts = 1000 * pts;
   //int64_t pts = (float) frame_count * (1000.0/(float)(FRAME_RATE)) * 90;
   int64_t pts = 1000 * d_->frameCount++;

   d_->videoPicture->pts = pts;

   int outSize = avcodec_encode_video(d_->videoCodecContext, d_->videoBuffer->data, d_->videoBufferSize, d_->videoPicture);
   if (outSize > 0) {
     // http://stackoverflow.com/questions/6603979/ffmpegavcodec-encode-video-setting-pts-h264
     //if (!isFixedFrameRate())
     AVPacket pkt;
     av_init_packet(&pkt);
     pkt.pts = pts;

     // This determine th speed;

     if (d_->videoCodecContext->coded_frame->key_frame)
       pkt.flags |= AV_PKT_FLAG_KEY;

     pkt.stream_index = d_->videoStream->index;
     pkt.data = d_->videoBuffer->data;
     pkt.size = outSize;
     av_write_frame(d_->formatContext, &pkt);
  }
  return true;
}

// Audio

bool AVRecorder::addAudioData(const uint8_t *data, int64_t size)
{
  return false;
}

// EOF
