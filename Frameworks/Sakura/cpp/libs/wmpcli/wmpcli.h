#pragma once

// wmpcli.h
// 10/1/2014 jichi

#ifdef _MSC_VER
# include <cstddef> // for wchar_t
#endif // _MSC_VER

// - Types -

struct IUnknown;
struct IWMPControls;
struct IWMPCore;
struct IWMPError;
struct IWMPMedia;
struct IWMPNetwork;
struct IWMPPlayer;
struct IWMPPlaylist;
struct IWMPSettings;

typedef IUnknown wmp_unknown_t;
typedef IWMPControls wmp_controls_t;
typedef IWMPCore wmp_core_t;
typedef IWMPError wmp_error_t;
typedef IWMPMedia wmp_media_t;
typedef IWMPNetwork wmp_network_t;
typedef IWMPPlayer wmp_player_t;
typedef IWMPPlaylist wmp_playlist_t;
typedef IWMPSettings wmp_settings_t;

// IWMPCore::get_playState
//typedef enum WMPPlayState {
//  wmppsUndefined      = 0,
//  wmppsStopped        = 1,
//  wmppsPaused         = 2,
//  wmppsPlaying        = 3,
//  wmppsScanForward    = 4,
//  wmppsScanReverse    = 5,
//  wmppsBuffering      = 6,
//  wmppsWaiting        = 7,
//  wmppsMediaEnded     = 8,
//  wmppsTransitioning  = 9,
//  wmppsReady          = 10,
//  wmppsReconnecting   = 11,
//  wmppsLast           = 12
//} WMPPlayState;

// IWMPCore::get_openState
//typedef enum WMPOpenState {
//  wmposUndefined                = 0,
//  wmposPlaylistChanging         = 1,
//  wmposPlaylistLocating         = 2,
//  wmposPlaylistConnecting       = 3,
//  wmposPlaylistLoading          = 4,
//  wmposPlaylistOpening          = 5,
//  wmposPlaylistOpenNoMedia      = 6,
//  wmposPlaylistChanged          = 7,
//  wmposMediaChanging            = 8,
//  wmposMediaLocating            = 9,
//  wmposMediaConnecting          = 10,
//  wmposMediaLoading             = 11,
//  wmposMediaOpening             = 12,
//  wmposMediaOpen                = 13,
//  wmposBeginCodecAcquisition    = 14,
//  wmposEndCodecAcquisition      = 15,
//  wmposBeginLicenseAcquisition  = 16,
//  wmposEndLicenseAcquisition    = 17,
//  wmposBeginIndividualization   = 18,
//  wmposEndIndividualization     = 19,
//  wmposMediaWaiting             = 20,
//  wmposOpeningUnknownURL        = 21
//} WMPOpenState;

// - Functions -

// Construction
wmp_player_t *wmp_player_create();
int wmp_release(void *p); // return reference count

wmp_controls_t *wmp_player_get_controls(wmp_player_t *p);
wmp_error_t *wmp_player_get_error(wmp_player_t *p);
wmp_settings_t *wmp_player_get_settings(wmp_player_t *p);
wmp_network_t *wmp_player_get_network(wmp_player_t *p);

wmp_playlist_t *wmp_player_get_playlist(wmp_player_t *p);
bool wmp_player_set_playlist(wmp_player_t *p, wmp_playlist_t *l);

wmp_media_t *wmp_player_get_media(wmp_player_t *p);
bool wmp_player_set_media(wmp_player_t *p, wmp_media_t *m);

// Core: http://msdn.microsoft.com/en-us/library/windows/desktop/dd563216%28v=vs.85%29.aspx
// Player: http://msdn.microsoft.com/en-us/library/windows/desktop/dd563514%28v=vs.85%29.aspx

bool wmp_player_close(wmp_player_t *p);

inline void wmp_player_destroy(wmp_player_t *p)
{
  if (p) {
    wmp_player_close(p);
    wmp_release(p);
  }
}

const wchar_t *wmp_player_get_version(wmp_player_t *p);

bool wmp_player_get_online(wmp_player_t *p);

bool wmp_player_set_enabled(wmp_player_t *p, bool t); // default true
bool wmp_player_get_enabled(wmp_player_t *p);

bool wmp_player_set_fullscreen(wmp_player_t *p, bool t); // default false
bool wmp_player_get_fullscreen(wmp_player_t *p);

bool wmp_player_set_contextmenuenabled(wmp_player_t *p, bool t); // default true
bool wmp_player_get_contextmenuenabled(wmp_player_t *p);

// Not sure why this function is not on MSDN
bool wmp_player_set_url(wmp_player_t *p, const wchar_t *val);
const wchar_t *wmp_player_get_url(wmp_player_t *p);

// None, invisible, full, minimal
bool wmp_player_set_uimode(wmp_player_t *p, const wchar_t *val);
const wchar_t *wmp_player_get_uimode(wmp_player_t *p);

// Settings: http://msdn.microsoft.com/en-us/library/windows/desktop/dd563648%28v=vs.85%29.aspx

// Whether display a dialog on error
bool wmp_settings_set_errordialogsenabled(wmp_settings_t *s, bool t); // default false
bool wmp_settings_get_errordialogsenabled(wmp_settings_t *s);

// Whether play on URL changes
bool wmp_settings_set_autostart(wmp_settings_t *s, bool t);
bool wmp_settings_get_autostart(wmp_settings_t *s);

// The prefix added to the URL
bool wmp_settings_set_baseurl(wmp_settings_t *s, const wchar_t *val);
const wchar_t *wmp_settings_get_baseurl(wmp_settings_t *s);

// [0,100] if succeed, or 0 if failed
enum { wmp_min_volume = 0, wmp_max_volume = 100 };
bool wmp_settings_set_volume(wmp_settings_t *s, int val);
int wmp_settings_get_volume(wmp_settings_t *s);

// [-100,100], default is 0
enum { wmp_min_balance = -100, wmp_max_balance = 100 };
bool wmp_settings_set_balance(wmp_settings_t *s, int val);
int wmp_settings_get_balance(wmp_settings_t *s);

// Whether has been muted
bool wmp_settings_set_mute(wmp_settings_t *s, bool t);
bool wmp_settings_get_mute(wmp_settings_t *s);

// Play speed, default is 1.0
bool wmp_settings_set_rate(wmp_settings_t *s, double val);
double wmp_settings_get_rate(wmp_settings_t *s);

// Number of times to play the same media. Default is 1. Return 0 if failed.
bool wmp_settings_set_playcount(wmp_settings_t *s, int val);
int wmp_settings_get_playcount(wmp_settings_t *s);

// Shuffle the order
bool wmp_settings_set_shuffle(wmp_settings_t *s, bool t);
bool wmp_settings_get_shuffle(wmp_settings_t *s);

// Repeat the tracks
bool wmp_settings_set_repeat(wmp_settings_t *s, bool t);
bool wmp_settings_get_repeat(wmp_settings_t *s);

// Play from the beginning when end is reached
bool wmp_settings_set_autorewind(wmp_settings_t *s, bool t);
bool wmp_settings_get_autorewind(wmp_settings_t *s);

// Controls: http://msdn.microsoft.com/en-us/library/windows/desktop/dd563179%28v=vs.85%29.aspx

bool wmp_controls_play(wmp_controls_t *c);
bool wmp_controls_stop(wmp_controls_t *c);
bool wmp_controls_pause(wmp_controls_t *c);

bool wmp_controls_previous(wmp_controls_t *c);
bool wmp_controls_next(wmp_controls_t *c);

bool wmp_controls_forward(wmp_controls_t *c);
bool wmp_controls_backward(wmp_controls_t *c);

// Seconds from the beginning. Return 0 if failed.
bool wmp_controls_set_pos(wmp_controls_t *c, double val);
double wmp_controls_get_pos(wmp_controls_t *c);

bool wmp_controls_set_media(wmp_controls_t *c, wmp_media_t *val);
wmp_media_t *wmp_controls_get_media(wmp_controls_t *c);

// Media: http://msdn.microsoft.com/en-us/library/windows/desktop/dd563397%28v=vs.85%29.aspx

// The two media are the same
bool wmp_media_equal(wmp_media_t *x, wmp_media_t *y);

// Return 0 if failed
double wmp_media_get_duration(wmp_media_t *m);

// Return nullptr if failed
const wchar_t *wmp_media_get_name(wmp_media_t *m);
bool wmp_media_set_name(wmp_media_t *m, const wchar_t *val);

// Return 0 if failed
int wmp_media_get_imagewidth(wmp_media_t *m);
int wmp_media_get_imageheight(wmp_media_t *m);

// Return nullptr if failed
const wchar_t *wmp_media_get_url(wmp_media_t *m);

// EOF
