namespace AITalkEditor
{
    using AITalk;
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.IO;
    using System.Windows.Forms;

    [Serializable]
    public class UserSettings
    {
        private string _constDbsPath;
        private string _constLangPath;
        private string _dbsPath;
        private string _langPath;
        public int BeginPause;
        public string CommonDirectoryPath;
        public VoiceSettings CommonVoice;
        public FindSettings Find;
        public bool HandleNewLineAsSentenceEnd;
        public List<string> IgnoredVoiceNames;
        public JeitaSettings Jeita;
        public string KanaDirectoryPath;
        public KanaFormat KanaMode;
        public float MasterVolume;
        public string SelectedVoiceName;
        public SoundOutputSettings SoundOutput;
        public int TermPause;
        public string TextDirectoryPath;
        public TextFormatSettings TextFormat;
        public bool UseCommonVoiceSettings;
        public UserDicSettings UserDic;
        public ViewSettings View;
        public List<VoiceSettings> Voice;
        public int VoiceSamplePerSec;
        public string WaveDirectoryPath;
        public WindowSettings Window;

        public UserSettings()
        {
            this.Initialize(new AppSettings());
        }

        public UserSettings(AppSettings appSettings)
        {
            this.Initialize(appSettings);
        }

        public void Initialize(AppSettings appSettings)
        {
            string folderPath = Environment.GetFolderPath(Environment.SpecialFolder.Personal);
            this.Window = new WindowSettings();
            this.View = new ViewSettings();
            this.CommonDirectoryPath = folderPath;
            this.TextDirectoryPath = folderPath;
            this.KanaDirectoryPath = folderPath;
            this.WaveDirectoryPath = folderPath;
            this.TextFormat = new TextFormatSettings();
            this.Find = new FindSettings();
            this.VoiceSamplePerSec = AppModeUtil.CheckSupport(appSettings.AppMode, AppMode.MicroVoice) ? 0x3e80 : 0x5622;
            if (appSettings.Function.UseConstVoiceDic)
            {
                this._constDbsPath = appSettings.Function.ConstVoiceDicPath;
            }
            else
            {
                this._constDbsPath = "";
                this.DbsPath = Path.Combine(Directory.GetParent(Application.StartupPath).FullName, "voice");
            }
            if (appSettings.Function.UseConstLangDic)
            {
                this._constLangPath = appSettings.Function.ConstLangDicPath;
            }
            else
            {
                this._constLangPath = "";
                this.LangPath = Path.Combine(Application.StartupPath, AppModeUtil.CheckSupport(appSettings.AppMode, AppMode.MicroLang) ? @"lang\normal" : "lang");
            }
            this.SoundOutput = new SoundOutputSettings(this.VoiceSamplePerSec);
            this.KanaMode = KanaFormat.AIKANA;
            this.IgnoredVoiceNames = new List<string>();
            this.SelectedVoiceName = "";
            this.UserDic = new UserDicSettings(appSettings);
            this.MasterVolume = 1f;
            this.BeginPause = 0;
            this.TermPause = 0;
            this.HandleNewLineAsSentenceEnd = true;
            this.UseCommonVoiceSettings = true;
            this.CommonVoice = new VoiceSettings();
            this.Voice = new List<VoiceSettings>();
            this.Jeita = new JeitaSettings();
        }

        public override string ToString()
        {
            return "未実装";
        }

        public bool Validate(AppSettings appSettings)
        {
            bool flag = false;
            string folderPath = Environment.GetFolderPath(Environment.SpecialFolder.Personal);
            if (this.Window == null)
            {
                this.Window = new WindowSettings();
                flag = true;
            }
            if (this.View == null)
            {
                this.View = new ViewSettings();
                flag = true;
            }
            if (this.CommonDirectoryPath == null)
            {
                this.CommonDirectoryPath = folderPath;
            }
            if (this.TextDirectoryPath == null)
            {
                this.TextDirectoryPath = folderPath;
            }
            if (this.KanaDirectoryPath == null)
            {
                this.KanaDirectoryPath = folderPath;
            }
            if (this.WaveDirectoryPath == null)
            {
                this.WaveDirectoryPath = folderPath;
            }
            if (this.TextFormat == null)
            {
                this.TextFormat = new TextFormatSettings();
                flag = true;
            }
            else
            {
                try
                {
                    new Font(this.TextFormat.FontFamilyName, this.TextFormat.Size, this.TextFormat.Style, this.TextFormat.Unit, this.TextFormat.GdiCharSet, this.TextFormat.GdiVerticalFont);
                }
                catch
                {
                    this.TextFormat = new TextFormatSettings();
                    flag = true;
                }
            }
            if (this.Find == null)
            {
                this.Find = new FindSettings();
                flag = true;
            }
            else
            {
                if ((this.Find.Target != FindSettings.TargetField.Text) && (this.Find.Target != FindSettings.TargetField.Yomi))
                {
                    this.Find.Target = FindSettings.TargetField.Text;
                    flag = true;
                }
                if ((this.Find.Logic != FindSettings.LogicalCondition.And) && (this.Find.Logic != FindSettings.LogicalCondition.Or))
                {
                    this.Find.Logic = FindSettings.LogicalCondition.And;
                    flag = true;
                }
                if (((this.Find.Match != FindSettings.MatchingCondition.Forward) && (this.Find.Match != FindSettings.MatchingCondition.Backward)) && (this.Find.Match != FindSettings.MatchingCondition.Partial))
                {
                    this.Find.Match = FindSettings.MatchingCondition.Partial;
                    flag = true;
                }
                if ((this.Find.PageSize < 1) || (this.Find.PageSize > 0xea60))
                {
                    this.Find.PageSize = 100;
                    flag = true;
                }
            }
            if ((this.VoiceSamplePerSec != 0x5622) && (this.VoiceSamplePerSec != 0x3e80))
            {
                this.VoiceSamplePerSec = AppModeUtil.CheckSupport(appSettings.AppMode, AppMode.MicroVoice) ? 0x3e80 : 0x5622;
                flag = true;
            }
            if (appSettings.Function.UseConstVoiceDic)
            {
                this._constDbsPath = appSettings.Function.ConstVoiceDicPath;
            }
            else
            {
                this._constDbsPath = "";
                if (this.DbsPath == null)
                {
                    this.DbsPath = Path.Combine(Directory.GetParent(Application.StartupPath).FullName, "voice");
                    flag = true;
                }
            }
            if (appSettings.Function.UseConstLangDic)
            {
                this._constLangPath = appSettings.Function.ConstLangDicPath;
            }
            else
            {
                this._constLangPath = "";
                if (this.LangPath == null)
                {
                    this.LangPath = Path.Combine(Application.StartupPath, AppModeUtil.CheckSupport(appSettings.AppMode, AppMode.MicroLang) ? @"lang\normal" : "lang");
                    flag = true;
                }
            }
            if (this.SoundOutput == null)
            {
                this.SoundOutput = new SoundOutputSettings(this.VoiceSamplePerSec);
                flag = true;
            }
            else
            {
                if ((this.SoundOutput.SamplePerSec != this.VoiceSamplePerSec) && (this.SoundOutput.SamplePerSec != (this.VoiceSamplePerSec / 2)))
                {
                    this.SoundOutput.SamplePerSec = this.VoiceSamplePerSec;
                    flag = true;
                }
                if (((this.SoundOutput.DataFormat != AIAudioFormatType.AIAUDIOTYPE_PCM_16) && (this.SoundOutput.DataFormat != AIAudioFormatType.AIAUDIOTYPE_MULAW_8)) || ((this.SoundOutput.DataFormat == AIAudioFormatType.AIAUDIOTYPE_MULAW_8) && (this.SoundOutput.SamplePerSec != 0x1f40)))
                {
                    this.SoundOutput.DataFormat = AIAudioFormatType.AIAUDIOTYPE_PCM_16;
                    flag = true;
                }
            }
            if ((this.KanaMode != KanaFormat.AIKANA) && (this.KanaMode != KanaFormat.JEITA))
            {
                this.KanaMode = KanaFormat.AIKANA;
                flag = true;
            }
            if (this.IgnoredVoiceNames == null)
            {
                this.IgnoredVoiceNames = new List<string>();
                flag = true;
            }
            if (this.SelectedVoiceName == null)
            {
                this.SelectedVoiceName = "";
                flag = true;
            }
            if (this.UserDic == null)
            {
                this.UserDic = new UserDicSettings(appSettings);
                flag = true;
            }
            else
            {
                if (this.UserDic.WordDicPath == null)
                {
                    this.UserDic.WordDicPath = appSettings.UserDic.DefaultWordDicFilePath;
                    flag = true;
                }
                if (this.UserDic.PhraseDicPath == null)
                {
                    this.UserDic.PhraseDicPath = appSettings.UserDic.DefaultPhraseDicFilePath;
                    flag = true;
                }
                if (this.UserDic.SymbolDicPath == null)
                {
                    this.UserDic.SymbolDicPath = appSettings.UserDic.DefaultSymbolDicFilePath;
                    flag = true;
                }
            }
            if ((this.MasterVolume < 0.01) || (this.MasterVolume > 5.0))
            {
                this.MasterVolume = 1f;
                flag = true;
            }
            if ((this.BeginPause < 0) || (this.BeginPause > 0x2710))
            {
                this.BeginPause = 0;
                flag = true;
            }
            if ((this.TermPause < 0) || (this.TermPause > 0x2710))
            {
                this.TermPause = 0;
                flag = true;
            }
            this.UseCommonVoiceSettings = true;
            if (this.CommonVoice == null)
            {
                this.CommonVoice = new VoiceSettings();
                flag = true;
            }
            else
            {
                if ((this.CommonVoice.Volume < 0.0) || (this.CommonVoice.Volume > 2.0))
                {
                    this.CommonVoice.Volume = 1f;
                    flag = true;
                }
                if ((this.CommonVoice.Speed < 0.5) || (this.CommonVoice.Speed > 4.0))
                {
                    this.CommonVoice.Speed = 1f;
                    flag = true;
                }
                if ((this.CommonVoice.Pitch < 0.5) || (this.CommonVoice.Pitch > 2.0))
                {
                    this.CommonVoice.Pitch = 1f;
                    flag = true;
                }
                if ((this.CommonVoice.Emphasis < 0.0) || (this.CommonVoice.Emphasis > 2.0))
                {
                    this.CommonVoice.Emphasis = 1f;
                    flag = true;
                }
                if ((this.CommonVoice.MiddlePause < 80) || (this.CommonVoice.MiddlePause > 500))
                {
                    this.CommonVoice.MiddlePause = 150;
                    flag = true;
                }
                if ((this.CommonVoice.LongPause < 100) || (this.CommonVoice.LongPause > 0x7d0))
                {
                    this.CommonVoice.LongPause = 370;
                    flag = true;
                }
                if ((this.CommonVoice.SentencePause < 200) || (this.CommonVoice.SentencePause > 0x2710))
                {
                    this.CommonVoice.SentencePause = 800;
                    flag = true;
                }
            }
            if (this.Voice == null)
            {
                this.Voice = new List<VoiceSettings>();
                flag = true;
            }
            else
            {
                this.Voice.Clear();
            }
            if (this.Jeita == null)
            {
                this.Jeita = new JeitaSettings();
                flag = true;
            }
            else
            {
                if (this.Jeita.FemaleVoiceName == null)
                {
                    this.Jeita.FemaleVoiceName = "";
                    flag = true;
                }
                if (this.Jeita.MaleVoiceName == null)
                {
                    this.Jeita.MaleVoiceName = "";
                    flag = true;
                }
                if ((this.Jeita.Sex == null) || ((this.Jeita.Sex != "F") && (this.Jeita.Sex != "M")))
                {
                    this.Jeita.Sex = "F";
                    flag = true;
                }
                if ((this.Jeita.Volume < 0) || (this.Jeita.Volume > 9))
                {
                    this.Jeita.Volume = 7;
                    flag = true;
                }
                if ((this.Jeita.Speed < 1) || (this.Jeita.Speed > 9))
                {
                    this.Jeita.Speed = 5;
                    flag = true;
                }
                if ((this.Jeita.Pitch < 1) || (this.Jeita.Pitch > 5))
                {
                    this.Jeita.Pitch = 3;
                    flag = true;
                }
                if ((this.Jeita.Emphasis < 0) || (this.Jeita.Emphasis > 3))
                {
                    this.Jeita.Emphasis = 2;
                    flag = true;
                }
                if ((this.Jeita.MiddlePause < 80) || (this.Jeita.MiddlePause > 300))
                {
                    this.Jeita.MiddlePause = 100;
                    flag = true;
                }
                if ((this.Jeita.LongPause < 100) || (this.Jeita.LongPause > 0x7d0))
                {
                    this.Jeita.LongPause = 300;
                    flag = true;
                }
                if ((this.Jeita.SentencePause < 300) || (this.Jeita.SentencePause > 0x2710))
                {
                    this.Jeita.SentencePause = 800;
                    flag = true;
                }
            }
            return !flag;
        }

        public string DbsPath
        {
            get
            {
                if (!(this._constDbsPath != ""))
                {
                    return this._dbsPath;
                }
                return this._constDbsPath;
            }
            set
            {
                this._dbsPath = value;
            }
        }

        public string LangPath
        {
            get
            {
                if (!(this._constLangPath != ""))
                {
                    return this._langPath;
                }
                return this._constLangPath;
            }
            set
            {
                this._langPath = value;
            }
        }

        public class FindSettings
        {
            public LogicalCondition Logic = LogicalCondition.And;
            public MatchingCondition Match = MatchingCondition.Partial;
            public int PageSize = 100;
            public TargetField Target = TargetField.Text;

            public enum LogicalCondition
            {
                And,
                Or
            }

            public enum MatchingCondition
            {
                Forward,
                Partial,
                Backward
            }

            public enum TargetField
            {
                Text,
                Yomi
            }
        }

        public class JeitaSettings
        {
            public int Emphasis = 2;
            public string FemaleVoiceName = "";
            public int LongPause = 300;
            public string MaleVoiceName = "";
            public int MiddlePause = 100;
            public int Pitch = 3;
            public int SentencePause = 800;
            public string Sex = "F";
            public int Speed = 5;
            public int Volume = 7;
        }

        public enum KanaFormat
        {
            AIKANA,
            JEITA
        }

        public class SoundOutputSettings
        {
            public AIAudioFormatType DataFormat;
            public bool FileHeader;
            public int SamplePerSec;
            public bool SaveText;

            public SoundOutputSettings()
            {
                this.SamplePerSec = 0x5622;
                this.DataFormat = AIAudioFormatType.AIAUDIOTYPE_PCM_16;
                this.FileHeader = true;
                this.SaveText = true;
            }

            public SoundOutputSettings(int samplePerSec)
            {
                this.SamplePerSec = samplePerSec;
                this.DataFormat = AIAudioFormatType.AIAUDIOTYPE_PCM_16;
                this.FileHeader = true;
                this.SaveText = true;
            }
        }

        public class TextFormatSettings
        {
            public string FontFamilyName = "MS UI Gothic";
            public Color ForeColor = Color.Black;
            public byte GdiCharSet = 0x80;
            public bool GdiVerticalFont = false;
            public float Size = 9f;
            public FontStyle Style = FontStyle.Regular;
            public GraphicsUnit Unit = GraphicsUnit.Point;
            public bool WordWrap = true;
        }

        public class UserDicSettings
        {
            public bool PhraseDicEnabled;
            public string PhraseDicPath;
            public bool SymbolDicEnabled;
            public string SymbolDicPath;
            public bool WordDicEnabled;
            public string WordDicPath;

            public UserDicSettings()
            {
                this.WordDicEnabled = true;
                this.PhraseDicEnabled = true;
                this.SymbolDicEnabled = true;
                this.WordDicPath = "";
                this.PhraseDicPath = "";
                this.SymbolDicPath = "";
            }

            public UserDicSettings(AppSettings appSettings)
            {
                this.WordDicEnabled = true;
                this.PhraseDicEnabled = true;
                this.SymbolDicEnabled = true;
                this.WordDicPath = appSettings.UserDic.DefaultWordDicFilePath;
                this.PhraseDicPath = appSettings.UserDic.DefaultPhraseDicFilePath;
                this.SymbolDicPath = appSettings.UserDic.DefaultSymbolDicFilePath;
            }
        }

        public class ViewSettings
        {
            public bool SettingsPaneVisible = true;
            public bool TuningPaneVisible = true;
        }

        public class VoiceSettings
        {
            public float Emphasis = 1f;
            public int LongPause = 370;
            public int MiddlePause = 150;
            public float Pitch = 1f;
            public int SentencePause = 800;
            public float Speed = 1f;
            public float Volume = 1f;
        }

        public class WindowSettings
        {
            public int Height = 720;
            public int Width = 0x3e8;
            public int X = 0;
            public int Y = 0;
        }
    }
}

