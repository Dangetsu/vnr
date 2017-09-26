namespace AITalkEditor
{
    using Microsoft.VisualBasic;
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.IO;
    using System.Windows.Forms;

    public class AppSettings
    {
        public Bitmap AppLogo;
        public AITalkEditor.AppMode AppMode;
        public string AuthCode;
        public bool AuthCodeFixed;
        public string ComporateName;
        public string ComporateName2;
        public string Copyright;
        public Bitmap CorporateLogo;
        public string Edition;
        public bool ExpirationDateVisible;
        public int FeatureID;
        public FunctionSettings Function;
        public System.Drawing.Icon Icon;
        public string LicenseFileName;
        public string LicenseKeyRegistryRootPath;
        public string LicenseKeyRegistryValueName;
        public LogOutoutMode LogOutput;
        public MenuSettings Menu;
        public NGWordSettings NGWord;
        public uint SoundBufferLatency;
        public int SoundBufferLength;
        public string SubTitle;
        public uint Timeout;
        public string Title;
        public TitleViewSettings TitleView;
        public UserDicSettings UserDic;
        public string Version;
        public Bitmap VersionInfoImage;
        public ViewSettings View;

        public AppSettings()
        {
            this.Edition = "Editor";
            this.LicenseKeyRegistryRootPath = @"HKEY_CURRENT_USER\Software\AI\AITalkII";
            this.LicenseKeyRegistryValueName = "edocesnecil";
            this.LicenseFileName = "aitalk.lic";
            this.AuthCode = "";
            this.Timeout = 0x3e8;
            this.SoundBufferLatency = 50;
            this.SoundBufferLength = 4;
            this.Title = "";
            this.SubTitle = "";
            this.Version = AssemblyInfoGetter.Version;
            this.ComporateName = "株式会社エーアイ";
            this.ComporateName2 = "";
            this.Copyright = AssemblyInfoGetter.Copyright;
            this.ExpirationDateVisible = true;
            this.TitleView = new TitleViewSettings();
            this.Function = new FunctionSettings();
            this.NGWord = new NGWordSettings();
            this.UserDic = new UserDicSettings();
            this.Menu = new MenuSettings();
            this.View = new ViewSettings();
        }

        public AppSettings(string[] args)
        {
            this.Edition = "Editor";
            this.LicenseKeyRegistryRootPath = @"HKEY_CURRENT_USER\Software\AI\AITalkII";
            this.LicenseKeyRegistryValueName = "edocesnecil";
            this.LicenseFileName = "aitalk.lic";
            this.AuthCode = "";
            this.Timeout = 0x3e8;
            this.SoundBufferLatency = 50;
            this.SoundBufferLength = 4;
            this.Title = "";
            this.SubTitle = "";
            this.Version = AssemblyInfoGetter.Version;
            this.ComporateName = "株式会社エーアイ";
            this.ComporateName2 = "";
            this.Copyright = AssemblyInfoGetter.Copyright;
            this.ExpirationDateVisible = true;
            this.TitleView = new TitleViewSettings();
            this.Function = new FunctionSettings();
            this.NGWord = new NGWordSettings();
            this.UserDic = new UserDicSettings();
            this.Menu = new MenuSettings();
            this.View = new ViewSettings();
            if ((args.Length > 0) && ((args[0] == "--log") || (args[0] == "-l")))
            {
                this.LogOutput |= LogOutoutMode.File;
            }
        }

        public string GetVersion(int dim)
        {
            if (dim < 1)
            {
                dim = 1;
            }
            string[] strArray = this.Version.Split(new char[] { '.' });
            if (dim > strArray.Length)
            {
                dim = strArray.Length;
            }
            return string.Join(".", strArray, 0, dim);
        }

        public string FullTitle
        {
            get
            {
                if (!(this.SubTitle != ""))
                {
                    return this.Title;
                }
                return (this.Title + " " + this.SubTitle);
            }
        }

        public string LicenseKeyRegistryKeyPath
        {
            get
            {
                return Path.Combine(Path.Combine(this.LicenseKeyRegistryRootPath, this.Edition), this.GetVersion(2));
            }
        }

        public class FunctionSettings
        {
            public string ConstLangDicPath = Path.Combine(Application.StartupPath, "lang");
            public string ConstVoiceDicPath = Path.Combine(Application.StartupPath, "voice");
            public string ConstVoiceName = "";
            public bool LangDicSettingsEnabled = true;
            public bool SoundOutputFormatSettingsEnabled = true;
            public bool UseConstLangDic;
            public bool UseConstVoiceDic;
            public bool VoiceDicSelectionEnabled = true;
        }

        public enum LogOutoutMode
        {
            None,
            Window,
            File
        }

        public class MenuSettings
        {
            public bool LangDicSettingVisible = true;
            public string OperatingManualText = "操作マニュアル(&H)";
            public bool RubySpecVisible = true;
            public bool SoundOutputSettingVisible = true;
            public string ViewSettingsText = "音声効果・ポーズ(&E)";
            public string ViewTuningText = "音声チューニング(&T)";
            public bool ViewVisible = true;
            public bool VoiceDicSettingVisible = true;
        }

        public class NGWordSettings
        {
            private Dictionary<string, string> _items;
            public bool Enabled;
            public string Message = "発話できない単語が含まれています。";

            public void SetItems(string[] value)
            {
                if (value == null)
                {
                    throw new ArgumentException("パラメータが不正です。");
                }
                this._items = new Dictionary<string, string>();
                for (int i = 0; i < value.Length; i++)
                {
                    string str = Strings.StrConv(value[i], VbStrConv.Wide, 0);
                    this._items[str] = str;
                }
            }

            public Dictionary<string, string> Items
            {
                get
                {
                    return this._items;
                }
            }
        }

        public class TitleViewSettings
        {
            public Point AppLogoLocation = new Point(11, 0x58);
            public Size AppLogoSize = new Size(0x178, 0x30);
            public PictureBoxSizeMode AppLogoSizeMode = PictureBoxSizeMode.CenterImage;
            public System.Drawing.Image Image;
            public Point ImageLocation;
            public Point SubTitleLocation;
            public Point TitleLocation;
            public bool VersionVisible = true;
        }

        public class UserDicSettings
        {
            public string DefaultPhraseDicDirName = "フレーズ辞書";
            public string DefaultPhraseDicFileName = "user.pdic";
            public string DefaultSymbolDicDirName = "記号ポーズ辞書";
            public string DefaultSymbolDicFileName = "user.sdic";
            public string DefaultUserDicDirName = "AITalkII";
            public string DefaultWordDicDirName = "単語辞書";
            public string DefaultWordDicFileName = "user.wdic";

            public string DefaultPhraseDicDirPath
            {
                get
                {
                    return Path.Combine(this.DefaultUserDicDirPath, this.DefaultPhraseDicDirName);
                }
            }

            public string DefaultPhraseDicFilePath
            {
                get
                {
                    return Path.Combine(this.DefaultPhraseDicDirPath, this.DefaultPhraseDicFileName);
                }
            }

            public string DefaultSymbolDicDirPath
            {
                get
                {
                    return Path.Combine(this.DefaultUserDicDirPath, this.DefaultSymbolDicDirName);
                }
            }

            public string DefaultSymbolDicFilePath
            {
                get
                {
                    return Path.Combine(this.DefaultSymbolDicDirPath, this.DefaultSymbolDicFileName);
                }
            }

            public string DefaultUserDicDirPath
            {
                get
                {
                    return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Personal), this.DefaultUserDicDirName);
                }
            }

            public string DefaultWordDicDirPath
            {
                get
                {
                    return Path.Combine(this.DefaultUserDicDirPath, this.DefaultWordDicDirName);
                }
            }

            public string DefaultWordDicFilePath
            {
                get
                {
                    return Path.Combine(this.DefaultWordDicDirPath, this.DefaultWordDicFileName);
                }
            }
        }

        public class ViewSettings
        {
            public ButtonImageSettings ButtonImage = new ButtonImageSettings();
            public bool DisplayLogo = true;
            public System.Drawing.Size MinimumSize = new System.Drawing.Size(800, 600);
            public PaneSettings SettingsPane = new PaneSettings(PaneType.Resizable, 400, 250, 6);
            public System.Drawing.Size Size = new System.Drawing.Size(0x400, 720);
            public System.Drawing.Size TextInputPaneMinSize = new System.Drawing.Size(300, 200);
            public PaneSettings TuningPane = new PaneSettings(PaneType.Resizable, 0x11a, 250, 6);
            public VoiceImageSettings VoiceImage = new VoiceImageSettings();

            public class ButtonImageSettings
            {
                public Image Clear;
                public Image Config;
                public Image Delete;
                public Image Dic;
                public Image Edit;
                public Image Exit;
                public Image New;
                public Image Pause;
                public Image Play;
                public Image Reg;
                public Image Save;
                public Image SaveWave;
                public Image Search;
                public Image Select;
                public Image Stop;
                public Image Time;
                public Image Tuning;
            }

            public class PaneSettings
            {
                private int _dockSize = 250;
                public int Size = 400;
                public int SplitterWidth = 6;
                public PaneType Type;

                public PaneSettings(PaneType type, int size, int minSize, int splitterWidth)
                {
                    this.Type = type;
                    this.Size = size;
                    this.DockSize = minSize;
                    this.SplitterWidth = splitterWidth;
                }

                public int DockSize
                {
                    get
                    {
                        if (this.Type != PaneType.Resizable)
                        {
                            return 0;
                        }
                        return this._dockSize;
                    }
                    set
                    {
                        this._dockSize = value;
                    }
                }
            }

            public class VoiceImageSettings
            {
                public Color BackColor = Color.White;
                public List<Image> ImageList = new List<Image>();
                public bool Visible;
            }
        }
    }
}

