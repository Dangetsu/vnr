#ifndef SSTAGS_H
#define SSTAGS_H

#ifdef _MSC_VER
# pragma warning (disable:4005)     // C4005: redefinition of SS_LEFT, SS_RIGHT on Windows
#endif // _MSC_VER

// sstags.h
// 7/15/2011 jichi

// - QSS syntax -

#define SS_BEGIN(id)    #id "{"
#define SS_END          "}"
#define SS_STMT_END     ";"
#define SS_URL_END      ");"

#define SS_NULL                     ";"
#define SS_PADDING_BEGIN            "padding:"
#define SS_PADDING(_len)            "padding:" #_len ";"
#define SS_NO_PADDING               SS_PADDING(0)
#define SS_TOP_BEGIN                "top:"
#define SS_TOP(_len)                "top:" #_len ";"
#define SS_BOTTOM_BEGIN             "bottom:"
#define SS_BOTTOM(_len)             "bottom:" #_len ";"
#define SS_LEFT_BEGIN               "left:"
#define SS_LEFT(_len)               "left:" #_len ";"
#define SS_RIGHT_BEGIN              "right:"
#define SS_RIGHT(_len)              "right:" #_len ";"
#define SS_IMAGE_BEGIN              "image:"
#define SS_IMAGE(_img)              "image:" #_img ";"
#define SS_IMAGE_URL_BEGIN          "image: url("
#define SS_IMAGE_URL(_url)          "image: url(" _url ");"
#define SS_BACKGROUND_BEGIN         "background:"
#define SS_BACKGROUND(_color)       "background:" #_color ";"
#define SS_BACKGROUND_COLOR_BEGIN   "background-color:"
#define SS_BACKGROUND_COLOR(_color) "background-color:" #_color ";"
#define SS_BACKGROUND_IMAGE_BEGIN   "background-image:"
#define SS_BACKGROUND_IMAGE(_img)   "background-image:" #_img ";"
#define SS_BACKGROUND_IMAGE_URL(_url)   "background-image: url(" _url ");"
#define SS_BACKGROUND_IMAGE_URL_BEGIN   "background-image: url("
#define SS_TRANSPARENT              "background:transparent;"
#define SS_SEMI_TRANSPARENT         SS_BACKGROUND_COLOR(rgba(0,0,0,1))
#define SS_POSITION_BEGIN           "position:"
#define SS_POSITION(_align)         "position:" #_align ";"
#define SS_POSITION_ABSOLUTE        SS_POSITION(absolute)
#define SS_POSITION_RELATIVE        SS_POSITION(relative)
#define SS_COLOR_BEGIN              "color:"
#define SS_COLOR(_color)            "color:" #_color ";"
#define SS_BORDER_COLOR_BEGIN       "border-color:"
#define SS_BORDER_COLOR(_color)     "border-color:" #_color ";"
#define SS_NO_BORDER                SS_BORDER(0)
#define SS_WIDTH_BEGIN              "width:"
#define SS_WIDTH(_len)              "width:" #_len ";"
#define SS_NO_WIDTH                 SS_WIDTH(0)
#define SS_HEIGHT_BEGIN             "height:"
#define SS_HEIGHT(_len)             "height:" #_len ";"
#define SS_NO_HEIGHT                SS_HEIGHT(0)
#define SS_BORDER_BEGIN             "border:"
#define SS_BORDER(_len)             "border:" #_len ";"
#define SS_BORDER_RADIUS_BEGIN      "border-radius:"
#define SS_BORDER_RADIUS(_len)      "border-radius:" #_len ";"
#define SS_BORDER_WIDTH_BEGIN       "border-width:"
#define SS_BORDER_WIDTH(_len)       "border-width:" #_len ";"
#define SS_BORDER_HEIGHT_BEGIN      "border-height:"
#define SS_BORDER_HEIGHT(_len)      "border-height:" #_len ";"
#define SS_BORDERLESS               "border-top:0;"
#define SS_MARGIN_BEGIN             "margin:"
#define SS_MARGIN(_len)             "margin:" #_len ";"
#define SS_MARGIN_LEFT_BEGIN        "margin-left:"
#define SS_MARGIN_LEFT(_len)        "margin-left:" #_len ";"
#define SS_MARGIN_RIGHT_BEGIN       "margin-right:"
#define SS_MARGIN_RIGHT(_len)       "margin-right:" #_len ";"
#define SS_MARGIN_TOP_BEGIN         "margin-top:"
#define SS_MARGIN_TOP(_len)         "margin-top:" #_len ";"
#define SS_MARGIN_BOTTOM_BEGIN      "margin-bottom:"
#define SS_MARGIN_BOTTOM(_len)      "margin-bottom:" #_len ";"
#define SS_NO_MARGIN                SS_MARGIN(0)
#define SS_BORDER_IMAGE_BEGIN       "border-image:"
#define SS_BORDER_IMAGE(_img)       "border-image:" #_img ";"
#define SS_BORDER_IMAGE_URL(_url)   "border-image: url(" _url ");"
#define SS_SELECTION_COLOR_BEGIN    "selection-color:"
#define SS_SELECTION_COLOR(_color)  "selection-color:" #_color ";"

#define SS_FONT_WEIGHT_BEGIN        "font-weight:"
#define SS_FONT_WEIGHT(_weight)     "font-weight:" #_weight ";"
#define SS_FONT_STYLE_BEGIN         "font-style:"
#define SS_FONT_STYLE(_style)       "font-style:" #_style ";"
#define SS_FONT_SIZE_BEGIN          "font-size:"
#define SS_FONT_SIZE(_size)         "font-size:" #_size ";"
#define SS_TEXT_DECORATION_BEGIN    "text-decoration:"
#define SS_TEXT_DECORATION(_d)      "text-decoration:" #_d ";"
#define SS_TEXT_ALIGN_BEGIN         "text-align:"
#define SS_TEXT_ALIGN(_a)           "text-align:" #_a ";"
#define SS_BOLD                     SS_FONT_WEIGHT(bold)
#define SS_ITALIC                   SS_FONT_STYLE(italic)
#define SS_UNDERLINE                SS_FONT_DECORATION(underline)
#define SS_OVERLINE                 SS_TEXT_DECORATION(overline)
#define SS_BLINK                    SS_TEXT_DECORATION(blink)
#define SS_STRIKE                   SS_TEXT_DECORATION(line-through)

#define SS_SUBCONTROL_POSITION_BEGIN    "subcontrol-position:"
#define SS_SUBCONTROL_POSITION(_align)  "subcontrol-position:" #_align ";"
#define SS_SUBCONTROL_ORIGIN_BEGIN      "subcontrol-origin:"
#define SS_SUBCONTROL_ORIGIN(_origin)   "subcontrol-origin:" #_origin ";"
#define SS_SUBCONTROL_ORIGIN_CONTENT    SS_SUBCONTROL_ORIGIN(content)
#define SS_SUBCONTROL_ORIGIN_PADDING    SS_SUBCONTROL_ORIGIN(padding)
#define SS_SUBCONTROL_ORIGIN_MARGIN     SS_SUBCONTROL_ORIGIN(margin)

#ifdef QT_CORE_LIB

#include <QtCore/QString>
inline QString ss_background_image_url(const QString &url)
{ return SS_BACKGROUND_IMAGE_URL_BEGIN + url + SS_URL_END; }

#endif // QT_CORE_LIB

#endif // SSTAGS_H
