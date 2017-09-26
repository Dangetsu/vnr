# coding: utf8
# info.py
# 6/5/2013 jichi

from mytr import my
import config

MAIL = config.EMAIL_HELP
BBCODE = "http://en.wikipedia.org/wiki/BBCode"
REGEX = "http://en.wikipedia.org/wiki/Regular_expression"

def renderCredits():
  import rc
  return rc.haml_template('haml/reader/credits').render()

def renderAppHelp():
  import rc
  return rc.haml_template('haml/reader/help').render()

#def renderAppHelp():
#  demo_url = config.URL_READER_DEMO
#  return "<br/><center>%s</center>" % (my.tr(
#"""
#Here's a walkthrough on youtube that might be helpful: <br/>
#<a href="%s">%s</a>
#<br/><br/>
#
#If you have got problems or suggestions, <br/>
#feel free to complain to me (<a href="mailto:%s">%s</a>) &gt;_&lt;""")
#% (demo_url, demo_url, MAIL, MAIL))

def renderAccountHelp():
  return (my.tr(
"""<h4>About the account</h4>
You don't need an account to access machine translations and subtitles from others.<br/>
<br/>
The account is only used to sign your subtitles with your ownership.
Other people can override your subtitle with a better one.
But they cannot directly edit or delete it without your permission.
If you would like to contribute to the game translation, you can get an account here:
<a href="%s">%s</a>

<h4>About the language</h4>
The language you select will determine:<br/>
* this app's language (en,ja,zh)<br/>
* the language of the machine translation<br/>
* the language of the subtitles you submit<br/>
* the dictionary used by the spell checker (en,fr,de)<br/>
* filter the shared dictionary entries

<h4>About the color</h4>
It color will be used to render your shared subtitles visible to others.

<h4>About the gender</h4>
In TTS, may I call you お兄ちゃん or 姉うえ? &gt; &lt;

<h4>About user privilege</h4>
VNR is standing on the shoulder of a large amount of user-shared contributions.
User privilege describes what you can do to other users' efforts (like subs) with/without their permissions.""")
% ("http://sakuradite.com", "http://sakuradite.com"))

def renderGameAgentHelp():
  return my.tr(
"""<h3>Explanation of the options</h3>
* Disable: leave the text unchanged<br/>
* Transcode: display the text and try to fix its encoding<br/>
* Translate: display the translation<br/>
* Both: display both the text and its translation<br/>
* Hide: display nothing<br/>

<br/>
This feature is currently under development and only supports a small portion of the games that ITH supports.
More information could be found on the Wiki:
<center>
<a href="http://sakuradite.com/wiki/en/VNR/Embedded_Translation">http://sakuradite.com/wiki/en/VNR/Embedded_Translation</a>
</center>

<h3>Language limitations</h3>
For SHIFT-JIS games, if you want to enable displaying translations into the game,
depending on which language you are speaking, it could result in lots of problems.
<br/>
A. Subset of Japanese: English and other Latin-based languages<br/>
B. Superset of Japanese: Simplified Chinese<br/>
C. Intersects Japanese: Traditional Chinese, Korean<br/>
D. Independent from Japanese: Thai<br/>
For type A languages, there is no problem. You can ignore this limitation section.<br/>
For Type D languages, there is currently no way to correctly embed the translation.<br/>
For both type B and C languages, VNR has to launch the game in your native locale than Japanese.<br/>
For Type B languages, there is no problem if the game is able to start in your locale.<br/>
For Type C languages, there will be encoding issue that the untranslated Japanese text could become garbage characters.<br/>

<h3>Debug</h3>
If this feature crashes your game, please try starting VNR using Debug VNR,
and there will be a vnragent.log file generated in VNR's directory.""")

def renderTextReaderHelp():
  return my.tr(
"""<h3>Introduction</h3>
Text Reader can translate the Japanese text under mouse.
For example, it can translate hovered Japanese Wikipedia articles in Firefox, online visual novels, or light novel paragraphs in Notepad.
This feature is in pre-alpha stage and has only primitive functionalities.
Any suggestions are welcomed!

<h3>Limitations</h3>
Only the text in traditional NORMAL window can be translated.
The current Text Reader cannot detect the window text that is rendered in non-native way.
For example, Text Reader can detect texts in game's menus, buttons, and dialogs,
but cannot detect texts rendered by GDI or DirectX.
Application-wise, Text Reader can work with Notepad, Internet Explore, and Firefox.
But it does not support Google Chrome and Foxit Reader.""")

def renderVoiceHelp():
  return my.tr(
"""<h3>Introduction</h3>
Usually, not all game characters are covered by voice actors.
In Voice Settings, you can assign specific TTS voice to the game character that does not have a CV.
VNR will read the texts only from selected game characters instead of speaking out all texts.
<br/><br/>

More information could be found on the Wiki:
<center>
<a href="http://sakuradite.com/wiki/en/VNR/Voice_Settings">http://sakuradite.com/wiki/en/VNR/Voice_Settings</a>
</center>

<h3>Usage</h3>
Character-aware TTS is not enabled by default.
You can enable it by first turning on TTS in Preferences/Voices,
and then clicking <span style="color:green">Enable</span> in Voice Settings.

<h3>Reading game text VS reading translation</h3>
By default, VNR will read the original game text.
However, if your selected TTS's language is the same as your language but different from game's language, VNR will read translations instead of game texts.
The translations could be either user-shared subtitles or machine translations in your language.

For example, after installing and enabling an English TTS, VNR could read English subtitles for you.

<h3>Recommended TTS software</h3>
TTS soft from VoiceText is recommended.
It supports not only Japanese, but also English, Chinese, and many other languages.""")

#<h3>Non-Japanese TTS</h3>
#When <span style="color:green">"Dub subtitles"</span> is the docked panel is checked,
#VNR will speak the subtitles in your language instead of the original Japanese game text.
#This might be helpful when you are too lazy to read the subtitles.

def renderReferenceHelp():
  return my.tr(
"""<h3>Motivation</h3>
In VNR, game settings including user-contributed subtitles and series-specific dictionary terms
are bound with the game's executable.
However, usually the same game has different versions of executables from
<span style="color:green">「初回版」,「通常版」,「廉価版」</span>, and different updates.
For example, if you have series-specific character names in the Shared Dictionary,
after the game is updated, the old terms might not work with the latest game anymore.
<br/><br/>
When that happens, you can create a reference for different versions of the same game.
<span style="color:purple">The games sharing the same reference will share the series-specific translations.</span>

<h3>Edit game references</h3>
Just open the Game Information from Spring Board,
click the <span style="color:green">Edit</span> button, search the game name,
select the current one, and press Save.
<br/><br/>
Then, you could find the game by refreshing the Game Information window.

<h3>Limitations</h3>
* Currently, only enterprise games on <a href="http://erogetrailers.com">ErogeTrailers.com</a>, <a href="http://amazon.co.jp">Amazon.co.jp</a>, or <a href="http://dmm.co.jp">DMM.co.jp</a> can be identified.
VNR cannot recognize games from other sites like doujin games on <a href="http://dlsite.com">DLsite.com</a>.
<br/>
* Each game can have at most one reference for each site.
<br/>
* Sometimes, there are multiple references of the same game.
Let's make some conventions on which one to keep, as follows:
<br/>
- The one that has the earliest release date
<br/>
- The one that has the highest price
<br/>
-「限定版」over「通常版」over「廉価版」etc.

<h3>Game site differences</h3>
You can add games from different sites. Some differences are as follows:
<br/>
* ErogeTrailers has the information of amazon and dmm, so that you don't have to add other sites manually.
<br/>
* Amazon has popular games, but no 同人 games and no latest 独占 games.
<br/>
DMM covers most of recent games, but is missing old games (say, before 2008).
<br/>
* DMM has more game information than Amazon, including authors and CGs.
<br/>
* You can only visit DMM web pages from Japan.

<h3>Improvement to Furigana and Machine Translation</h3>
After setting up online information for the game, VNR will be able to search character names specific for the game.
The character names will then be used to correct the furigana and machine translation for these names.
Current, there is no way to specify or edit the automatically detected character names.
If you don't like the translation for certain names, you can create a new term in the Shared Dictionary to override the existing ones.""")

def renderCommentHelp():
  return my.tr(
"""<h3>Introduction</h3>
VNR supports sharing <span style='color:purple'>annotations (danmaku, comments, and subtitles, etc.)</span> for game text.
That's why it is under the <span style='color:purple'>Annot(ation) Player</span> project.
Users can submit annotations while playing games.
Annotations will be saved online together with the user's signature, and the current <span style='color:green'>game context (current game and recent text)</span>.
When other users visit the same game context, VNR will render annotations to the screen.
The entire process is done WITHOUT modifying any original game files.
<br/><br/>
Comparing to fan translation by patching the game files,
annotations in VNR are kind of similar to external subtitles of video,
while patched translations are like embedded subtitles.
Regarding the translation quality, annotations are more like community-contributed wikis,
while patched translations are books written by closed groups of elite.

More information could be found on the Wiki:
<center>
<a href="http://sakuradite.com/wiki/en/VNR/Sharing_Subtitles">http://sakuradite.com/wiki/en/VNR/Sharing_Subtitles</a>
</center>

<h3>Enable/disable annotations</h3>
Annotations are enabled by default.
If there are subtitles or comments from others, they will show up in the game automatically.
<br/><br/>
If you don't need annotation support,
you can either hide annotations in the left docked panel, or disable them in Preferences/Features.

<h3>Submit/Edit/Export Annotations</h3>
To submit a new subtitle, just launch the game, <span style="color:green">type in the submit bar in the bottom of the game window, and press Enter</span> .
You can also open Subtitle Maker to sub recent prevent game text,
<span style="color:red">
Internet access is required for adding or modifying subtitles.
</span>
<br/><br/>
You can edit existing subtitles by right-clicking it, and select edit.
You can also revise and edit existing subtitles in Subtitle Editor, or recent subtitles in Subtitle Maker.
<br/><br/>
You can export existing subtitles into CSV files in Subtitle Editor.""")

def renderTermHelp():
  #wiki = 'http://sakuradite.com/wiki/en/VNR/Shared Dictionary'
  #motivation_url = "http://amaenboda.wordpress.com/2012/03/26/an-aero-gamers-guide-to-using-atlas/5/#Replacement%20Script%20and%20Other%20Add%20Ons"
  return my.tr(
"""<h3>Introduction</h3>
This shared dictionary serves to improve machine translation for game texts and window texts.
It will not affect user-contributed subtitles.
The terms defined in the dictionary will be replaced in the text before or after machine translation.
The dictionary can be a double-edged sword and be careful that don't let it hurt you &gt;_&lt;

More information could be found on the Wiki:
<center>
<a href="http://sakuradite.com/wiki/en/VNR/Shared_Dictionary">http://sakuradite.com/wiki/en/VNR/Shared_Dictionary</a>
</center>

<h3>Usage</h3>
<span style="color:green">
Just press "New" to add a new entry, and edit "pattern" and "translation" columns.
Then, VNR will replace "pattern" with the "translation" in new subtitles and window texts.
</span>
Editable cells are in <span style="color:green">green color</span>.
Read-only columns are in <span style="color:steelblue">blue color</span>.
<br/><br/>

<span style="color:red">
Internet access is required for adding or modifying the entries in the dictionary,
so that all the changes could be saved online.
</span>
When offline, the dictionary will become read-only.
VNR will automatically update the dictionary every a few days.
But you can also press "Refresh" to run the update manually.""")

def renderTextSettingsHelp():
  #ascii_url = "http://en.wikipedia.org/wiki/ASCII"
  #help_url_zh = "http://tieba.baidu.com/f?kw=%DF%F7%B7%AD"
  return my.tr(
"""<h3>Introduction</h3>
In Text Settings and Game Wizard,
you can select which text threads to display and translate in VNR.
If after synchronizing with the game, no text appears in VNR,
it is usually because your text settings for the game is inappropriate.

More information could be found on the Wiki:
<center>
<a href="http://sakuradite.com/wiki/en/VNR/Text_Settings">http://sakuradite.com/wiki/en/VNR/Text_Settings</a>
</center>

<h3>Text Threads</h3>
A game might have one or a couple of text threads.
You might want to identify those EXACTLY THE SAME AS THE GAME TEXT.
In VNR, you can categorize the text threads into three kinds:
<br/>
* <span style="color:purple">Dialog</span>: This text thread is the scenario thread.
<br/>
* <span style="color:purple">Chara</span>: The contents are names of game characters.
<br/>
* <span style="color:purple">Other</span>: The text thread is neither dialogue nor character, but still translate it.
<br/>
* <span style="color:purple">Ignore</span>: Do not translate this text thread.
<br/>
<span style="color:green">The game must have exact ONE dialogue text thread.</span>
And it could have at most ONE character text thread.
But you can specify multiple other text threads.

<h3>Text Speed</h3>
I strongly recommend you to <span style="color:red">adjust the game's <b>TEXT SPEED TO MAXIMUM</b></span>.
It will enhance both the speed and the correctness of game text detection.
<span style="color:green">If the text threads are <b>FRAGMENTED</b>, or there are <b>NO SPACES</b> in the words (esp. for English galgame),
it is usually the outcome of a slow text speed.</span>
<br/><br/>

Usually, you can adjust the game's text speed in <span style="color:purple">「コンフィグ」</span>(Config) or <span style="color:purple">「設定」</span>(Settings).
The text speed option is usually a draggable slider labeled by <span style="color:purple">「テキスト速度」</span>(Text Speed).

<h3>Game Font</h3>
If there is no game text appearing, adjusting game font might help.
For example, VNR could not detect the game text in <span style="color:purple">「時計仕掛けのレイライン」</span>
unless you have changed its font from MS Mincho (MS明朝) to <span style="color:red">MS Gothic (MSゴシック)</span>.

<h3>Hook Code</h3>
If no correct text thread appears even after adjusting Text Speed,
you might have to edit the hook code specific for this game.
Please click the "Edit Hook Code" button, and you can find more details there.
<br/><br/>

If the game crashes after applying the hook code,
<span style="color:red">especially with a C00005 exception dialog popping up</span>,
it means the current hook code does not work for this game.
Please click the "Edit Hook Code" button, and delete the criminal hook code.""")

def renderHookCodeHelp():
  #HCODE_HELP_URL = "https://www.google.com/#hl=en&safe=off&q=ITH%20hook%20code"
  HCODE_SEARCH_URL_1 = "http://agth.wikia.com/wiki/H-codes"
  HCODE_SEARCH_URL_2 = "http://blgames.proboards.com/post/1984"
  #HCODE_SEARCH_URL_3 = "http://agthdb.bakastyle.com"
  #CHEATENGINE_URL = "http://www.cheatengine.org"
  #CHEATENGINE_HELP_URL = "http://agth.wikia.com/wiki/Cheat_Engine_AGTH_Tutorial"
  #CHEATENGINE_HELP_URL_ZH = "http://user.qzone.qq.com/49755509"
  return (my.tr(
"""The hook code is a <i>hash string</i> encoded by the information needed to sync with specific game.
It is not required by all the games, but is essential for some ones.
It is a string that always starts with <span style="color:green">"/H"</span>.
<br/><br/>

If you have already got a good text thread, you can ignore the following text.
Otherwise, you have to search for the correct hook code specific for the game, and type it here.
<br/><br/>

Here's an example hook code for 「恋と選挙とチョコレート」:
<center style="color:green">/HSN-4@B14B4:dirapi.dll</center>

You can find most game-specific hook code from these places:
<center><a href="{0}">{0}</a></center>
<center><a href="{1}">{1}</a></center>
<br/>

Only /H code is supported, and other AGTH parameters are not supported (such as /P).
I mean, there should be NO SPACES within the hook code.
Contents after spaces will be ignored.
<br/><br/>

Some games might not need H-code, but the game settings have to be adjusted.
Check this wiki for what to do if there is no correct text.
<center><a href="http://sakuradite.com/wiki/en/VNR/Game_Settings">http://sakuradite.com/wiki/en/VNR/Game_Settings</a></center>""")
.format(
  HCODE_SEARCH_URL_1,
  HCODE_SEARCH_URL_2,
))

def renderEmbeddedTextSettingsHelp():
  #ascii_url = "http://en.wikipedia.org/wiki/ASCII"
  #help_url_zh = "http://tieba.baidu.com/f?kw=%DF%F7%B7%AD"
  return my.tr(
"""<h3>Introduction</h3>
In Text Settings, you can identify which text threads to display and translate.
If after synchronizing with the game, no texts appear in VNR,
it is usually because your text settings for the game is inappropriate.
<br/><br/>

This is the Text Settings for VNR's experimental embedded text hook rather than ITH.
VNR's text hook allows embedding translations into the game, but it supports much fewer games than ITH.
Additionally, <span style="color:red">VNR's text hook does NOT support H-code</span>.
You can adjust which text hook to use in Preferences/Embed.
The game is needed to be restarted after the text hook is changed.

<h3>Text Threads</h3>
A game might have one or a couple of text threads.
You might want to identify those EXACTLY THE SAME AS THE GAME TEXT.
Two kinds of text threads are currently supported.
<br/>
* <span style="color:purple">Dialog</span>: This text thread is the scenario thread.
<br/>
* <span style="color:purple">Chara</span>: The contents are names of game characters.
<br/>
<span style="color:green">The game must have exact ONE dialogue text thread.</span>
And it could have at most ONE character text thread.

<h3>Game Engine</h3>
Embedding translation might not work well for all games.
Certain game engines might have their specific issues.
More information could be found on the Wiki:
<center>
<a href="http://sakuradite.com/wiki/en/VNR/Game_Engine">http://sakuradite.com/wiki/en/VNR/Game_Engine</a>
</center>

<!--
<h3>Text Speed</h3>
Different from ITH, the text speed of the game does NOT matter.
It is OK if you adjust the text speed to slow.
-->

<h3>Hook Code</h3>
Different from ITH, the H-code is NOT supported.

<h3>Debug Output</h3>
If VNR is launched from "Debug VNR.cmd", VNR's text hook will save the debug log into "vnragent.log" file in VNR's directory.
If the game crashes because of VNR, you might be able to find the reason of the crash in that log file.""")

# EOF
