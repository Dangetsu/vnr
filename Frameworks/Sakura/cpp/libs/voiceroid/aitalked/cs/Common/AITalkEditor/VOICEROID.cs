namespace AITalkEditor
{
    using AITalkEditor.Properties;
    using System;
    using System.Drawing;

    public class VOICEROID
    {
        public static AppSettings CreateAppSettings(string[] args)
        {
            AppSettings settings = new AppSettings(args) {
                Edition = "VOICEROID",
                AuthCodeFixed = true,
                AppMode = AppMode.VoiceArtist,
                Title = "VOICEROID＋",
                ComporateName = "販売 : 株式会社ＡＨＳ",
                ComporateName2 = "開発 : 株式会社エーアイ",
                CorporateLogo = AITalkEditor.Properties.Resources.corporate_logo_s,
                ExpirationDateVisible = false
            };
            settings.TitleView.ImageLocation = new Point(0x120, 80);
            settings.TitleView.VersionVisible = false;
            settings.Function.UseConstVoiceDic = true;
            settings.Function.UseConstLangDic = true;
            settings.Function.SoundOutputFormatSettingsEnabled = false;
            settings.UserDic.DefaultUserDicDirName = "VOCEROID＋";
            settings.Menu.VoiceDicSettingVisible = false;
            settings.Menu.ViewVisible = true;
            settings.Menu.RubySpecVisible = false;
            settings.Menu.ViewSettingsText = "キャラクタ(&C)";
            settings.Menu.OperatingManualText = "VOICEROID＋ ヘルプ(&H)";
            settings.View.DisplayLogo = false;
            settings.View.Size = new Size(800, 640);
            settings.View.MinimumSize = new Size(640, 540);
            settings.View.TextInputPaneMinSize = new Size(0, 0);
            settings.View.VoiceImage.Visible = true;
            settings.View.TuningPane.Type = PaneType.Removable;
            settings.View.SettingsPane.Type = PaneType.Removable;
            settings.View.SettingsPane.Size = 0xb6;
            settings.View.ButtonImage.Clear = AITalkEditor.Properties.Resources.clear;
            settings.View.ButtonImage.Config = AITalkEditor.Properties.Resources.config;
            settings.View.ButtonImage.Delete = AITalkEditor.Properties.Resources.delete;
            settings.View.ButtonImage.Dic = AITalkEditor.Properties.Resources.dic;
            settings.View.ButtonImage.Edit = AITalkEditor.Properties.Resources.edit;
            settings.View.ButtonImage.Exit = AITalkEditor.Properties.Resources.exit;
            settings.View.ButtonImage.New = AITalkEditor.Properties.Resources._new;
            settings.View.ButtonImage.Pause = AITalkEditor.Properties.Resources.pause;
            settings.View.ButtonImage.Play = AITalkEditor.Properties.Resources.play;
            settings.View.ButtonImage.Reg = AITalkEditor.Properties.Resources.reg;
            settings.View.ButtonImage.Save = AITalkEditor.Properties.Resources.save;
            settings.View.ButtonImage.SaveWave = AITalkEditor.Properties.Resources.save;
            settings.View.ButtonImage.Search = AITalkEditor.Properties.Resources.search;
            settings.View.ButtonImage.Select = AITalkEditor.Properties.Resources.select;
            settings.View.ButtonImage.Stop = AITalkEditor.Properties.Resources.stop;
            settings.View.ButtonImage.Time = AITalkEditor.Properties.Resources.time;
            settings.View.ButtonImage.Tuning = AITalkEditor.Properties.Resources.tuning;
            return settings;
        }
    }
}

