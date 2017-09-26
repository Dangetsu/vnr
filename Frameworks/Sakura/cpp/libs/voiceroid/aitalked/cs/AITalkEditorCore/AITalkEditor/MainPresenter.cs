namespace AITalkEditor
{
    using AITalk;
    using AITalkTuning;
    using Microsoft.VisualBasic;
    using Microsoft.Win32;
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Drawing;
    using System.IO;
    using System.Runtime.InteropServices;
    using System.Text;
    using System.Text.RegularExpressions;
    using System.Threading;
    using System.Windows.Forms;

    public class MainPresenter : ApplicationContext, IMainController, IVoiceDicSettingController, ILangDicSettingController, ISoundOutputSettingController, IKanaSettingController, IUserDicController, IFindSettingController, ITextFormatSettingController, IViewSettingController, IVersionInfoController
    {
        private AITalkUtilEx _aitalk;
        private AppSettings _appSettings;
        private AppVariables _appVariables = new AppVariables();
        private DongleAuth _dongleAuth;
        private LogView _logView;
        private PhraseDic _phraseDic;
        private SettingsManager _settingsManager;
        private SymbolDic _symbolDic;
        private UserDicView _userDicView;
        private MainView _view;
        private WordDic _wordDic;
        public const int SW_SHOWNORMAL = 1;

        public MainPresenter(AppSettings appSettings)
        {
            this._appSettings = appSettings;
            if ((AITalkEditorAPI.ModuleFlag() & 2) == 2)
            {
                this._appSettings.AppMode |= AppMode.MicroLang;
                this._appSettings.AppMode &= ~AppMode.PhraseDicSupport;
                this._appSettings.AppMode &= ~AppMode.PhraseEditSupport;
                this._appSettings.AppMode &= ~AppMode.SymbolDicSupport;
                this._appSettings.AppMode &= ~AppMode.SymbolEditSupport;
            }
            if ((AITalkEditorAPI.ModuleFlag() & 1) == 1)
            {
                this._appSettings.AppMode |= AppMode.MicroVoice;
            }
            this._settingsManager = new SettingsManager();
            this._settingsManager.Settings = new UserSettings(this._appSettings);
            if (File.Exists(Common.UserSettingsFilePath))
            {
                try
                {
                    this._settingsManager.Read(Common.UserSettingsFilePath, this._appSettings);
                }
                catch (Exception exception)
                {
                    MessageBox.Show("設定ファイルの読み込みに失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                }
            }
            this._aitalk = AITalkUtilEx.GetInstance();
            this.InitializeAppMode();
            this._phraseDic = new PhraseDic();
            this._wordDic = new WordDic();
            this._symbolDic = new SymbolDic();
            this._userDicView = new UserDicView(this, this._appSettings, this._settingsManager.Settings, this._phraseDic, this._wordDic);
            this._view = new MainView(this._appSettings, this._settingsManager.Settings, this._appVariables);
            this._view.Attach(this);
            this._aitalk.AssociatedControl = this._view;
            if (this._appSettings.LogOutput != AppSettings.LogOutoutMode.None)
            {
                this._aitalk.WriteLog += new AITalkUtil.LogEventHandler(this.OnWriteLog);
            }
            if ((this._appSettings.LogOutput & AppSettings.LogOutoutMode.File) == AppSettings.LogOutoutMode.File)
            {
                this.WriteLogOnFile(string.Concat(new object[] { 
                    Environment.NewLine, "================================================================================", Environment.NewLine, "Title: ", this._appSettings.Title, Environment.NewLine, "Edition: ", this._appSettings.Edition, Environment.NewLine, "Version: ", this._appSettings.Version, Environment.NewLine, "DateTime: ", DateTime.Now, Environment.NewLine, "================================================================================", 
                    Environment.NewLine
                 }));
            }
            if ((this._appSettings.LogOutput & AppSettings.LogOutoutMode.Window) == AppSettings.LogOutoutMode.Window)
            {
                this._logView = new LogView();
                this._logView.Show(this._view);
            }
            this._aitalk.TextProcessingProgress += new AITalkUtilEx.TextProcessingEventHandler(this.OnTextProcessingProgress);
            this._aitalk.TextProcessingComplete += new AITalkUtilEx.TextProcessingEventHandler(this.OnTextProcessingComplete);
            this._aitalk.SynthesizingProgress += new AITalkUtilEx.SynthesizingEventHandler(this.OnSynthesizingProgress);
            this._aitalk.SynthesizingComplete = (AITalkUtilEx.SynthesizingEventHandler) Delegate.Combine(this._aitalk.SynthesizingComplete, new AITalkUtilEx.SynthesizingEventHandler(this.OnSynthesizingComplete));
            this._aitalk.PlaySentence += new AITalkUtilEx.AudioEventHandler(this.OnPlaySentence);
            if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.HighlightSupport))
            {
                this._aitalk.PlayBookmark += new AITalkUtilEx.AudioEventHandler(this.OnPlayBookmark);
            }
            this._aitalk.PlayPhonemeLabel += new AITalkUtilEx.PhonemeLabelEventHandler(this.OnPlayPhonemeLabel);
            this._aitalk.PlayComplete += new AITalkUtilEx.AudioEventHandler(this.OnPlayComplete);
            this._aitalk.ErrorOccured += new AITalkUtilEx.ErrorEventHandler(this.OnErrorOccured);
            this.Initialize();
        }

        public void AddPhrase(IWin32Window owner, PhraseEntry phraseEntry)
        {
            if (phraseEntry != null)
            {
                this._phraseDic.StartUpdate();
                if ((this._phraseDic.CheckExistence(phraseEntry) >= 0) && (DialogResult.Yes != MessageBox.Show(owner, "同じフレーズが既に登録されています。" + Environment.NewLine + "上書きしてよろしいですか？", "注意", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2)))
                {
                    this._phraseDic.EndUpdate();
                }
                else
                {
                    try
                    {
                        this._phraseDic.Add(phraseEntry, true);
                    }
                    catch (Exception exception)
                    {
                        MessageBox.Show(owner, "フレーズの登録に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                        this._phraseDic.EndUpdate();
                        return;
                    }
                    try
                    {
                        this._phraseDic.Write(this._settingsManager.Settings.UserDic.PhraseDicPath);
                    }
                    catch (Exception exception2)
                    {
                        MessageBox.Show(owner, "フレーズ辞書の書き込みに失敗しました。" + Environment.NewLine + exception2.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                        this._phraseDic.EndUpdate();
                        return;
                    }
                    this._phraseDic.EndUpdate();
                    this._view.PhraseChanged = false;
                    try
                    {
                        this.ReloadPhraseDic();
                    }
                    catch (Exception exception3)
                    {
                        MessageBox.Show(this._view, exception3.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                        return;
                    }
                    MessageBox.Show(owner, "フレーズを登録しました。", "情報", MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
                }
            }
        }

        public void AddWord(IWin32Window owner, WordEntry wordEntry)
        {
            if ((wordEntry != null) && (((wordEntry.Cost >= Common.CostList[Common.CostList.Length - 2].Threshold) || (wordEntry.Hinshi == HinshiCode.Symbol)) || (DialogResult.Yes == MessageBox.Show(owner, "優先度が「最高」に指定されています。" + Environment.NewLine + "優先度の高い単語は日本語解析に悪影響を与える可能性があります。" + Environment.NewLine + "登録してよろしいですか？", "注意", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2))))
            {
                this._wordDic.StartUpdate();
                if ((this._wordDic.CheckExistence(wordEntry) >= 0) && (DialogResult.Yes != MessageBox.Show(owner, "同じ単語が既に登録されています。" + Environment.NewLine + "上書きしてよろしいですか？", "注意", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2)))
                {
                    this._wordDic.EndUpdate();
                }
                else
                {
                    try
                    {
                        this._wordDic.Add(wordEntry, true);
                    }
                    catch (Exception exception)
                    {
                        MessageBox.Show(owner, "単語の登録に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                        this._wordDic.EndUpdate();
                        return;
                    }
                    try
                    {
                        this._wordDic.Write(this._settingsManager.Settings.UserDic.WordDicPath);
                    }
                    catch (Exception exception2)
                    {
                        MessageBox.Show(owner, "単語辞書の書き込みに失敗しました。" + Environment.NewLine + exception2.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                        this._wordDic.EndUpdate();
                        return;
                    }
                    this._wordDic.EndUpdate();
                    this._view.WordChanged = false;
                    if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.MicroLang))
                    {
                        this.InitializeLangDic(true, this._view, null, 0, 100);
                    }
                    else
                    {
                        try
                        {
                            this.ReloadWordDic();
                        }
                        catch (Exception exception3)
                        {
                            MessageBox.Show(this._view, exception3.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                            return;
                        }
                    }
                    MessageBox.Show(owner, "単語を登録しました。", "情報", MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
                }
            }
        }

        void IVersionInfoController.ChangeLicenseKey(Form owner)
        {
            using (LicenseKeyView view = new LicenseKeyView())
            {
                if (view.ShowDialog() == DialogResult.OK)
                {
                    try
                    {
                        this.WriteLicenseKey(view.LicenseKey);
                        goto Label_0051;
                    }
                    catch (Exception exception)
                    {
                        MessageBox.Show("ライセンスキーの保存に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    }
                }
                return;
            }
        Label_0051:
            if (MessageBox.Show(owner, "新しいライセンスキーは次回起動時に反映されます。" + Environment.NewLine + "プログラムを終了してよろしいですか？", "確認", MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2) == DialogResult.Yes)
            {
                this._view.Close();
            }
        }

        public void btnAddPhrase_Click(object sender, EventArgs e)
        {
            this.AddPhrase(this._view, this._view.PhraseEntry);
        }

        public void btnAddWord_Click(object sender, EventArgs e)
        {
            this.AddWord(this._view, this._view.WordEntry);
        }

        public void btnCalcWaveLength_Click(object sender, EventArgs e)
        {
            if (this.CheckDongleRuntime() && this.CheckNGWord(this._view.SynthText))
            {
                this.CalcWaveLength(SynthMode.TextToWave, this._view.SynthText);
                this._view.FocusMainText();
            }
        }

        public void btnCalcWaveLengthFromKana_Click(object sender, EventArgs e)
        {
            if (this.CheckDongleRuntime())
            {
                this.CalcWaveLength(SynthMode.Synthesize, this._view.KanaEdit);
                this._view.FocusKanaEdit();
            }
        }

        public void btnExecuteGC_Click(object sender, EventArgs e)
        {
            long totalMemory = GC.GetTotalMemory(false);
            GC.Collect();
            long num2 = GC.GetTotalMemory(false);
            MessageBox.Show(this._view, string.Concat(new object[] { "Before: ", totalMemory, Environment.NewLine, "After: ", num2 }), "GC", MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
        }

        public void btnGenerateKana_Click(object sender, EventArgs e)
        {
            if (((!this._view.KanaEditModified || (DialogResult.Yes == MessageBox.Show(this._view, "中間言語が変更されています。" + Environment.NewLine + "破棄してよろしいですか？", "注意", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2))) && this.CheckDongleRuntime()) && this.CheckNGWord(this._view.SynthText))
            {
                this.GenerateKana();
                this._view.FocusMainText();
            }
        }

        public void btnPlay_Click(object sender, EventArgs e)
        {
            if (this._view.ViewStatus == ViewStatusCode.Play)
            {
                this._view.ViewStatus = ViewStatusCode.Pause;
                this._aitalk.PauseAudio();
            }
            else if (this._view.ViewStatus == ViewStatusCode.Pause)
            {
                this._view.ViewStatus = ViewStatusCode.Play;
                this._aitalk.ResumeAudio();
            }
            else if (!this._view.ReadyToPlay())
            {
                this._view.FocusMainText();
            }
            else if (this.CheckDongleRuntime() && this.CheckNGWord(this._view.SpeechText))
            {
                this._view.ViewStatus = ViewStatusCode.Play;
                this.PrepareSynth();
                AITalkResultCode key = this._aitalk.Do(SynthMode.TextToSpeech, this._view.SpeechText, this.GetSynthOption(false));
                if (key != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    if (key != AITalkResultCode.AITALKERR_INVALID_ARGUMENT)
                    {
                        MessageBox.Show(this._view, "再生に失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(key), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    }
                    this._view.ViewStatus = ViewStatusCode.Edit;
                    this._view.FocusMainText();
                }
                else
                {
                    this._view.HighlightSetup();
                }
            }
        }

        public void btnPlayKana_Click(object sender, EventArgs e)
        {
            if (this._view.ViewStatus == ViewStatusCode.PlayKana)
            {
                this._view.ViewStatus = ViewStatusCode.PauseKana;
                this._aitalk.PauseAudio();
            }
            else if (this._view.ViewStatus == ViewStatusCode.PauseKana)
            {
                this._view.ViewStatus = ViewStatusCode.PlayKana;
                this._aitalk.ResumeAudio();
            }
            else if (this.CheckDongleRuntime())
            {
                this._view.ViewStatus = ViewStatusCode.PlayKana;
                this.PrepareSynth();
                AITalkResultCode key = this._aitalk.Do(SynthMode.KanaToSpeech, this._view.KanaEdit, this.GetSynthOption(false));
                if (key != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    if (key != AITalkResultCode.AITALKERR_INVALID_ARGUMENT)
                    {
                        MessageBox.Show(this._view, "再生に失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(key), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    }
                    this._view.ViewStatus = ViewStatusCode.Edit;
                    this._view.FocusKanaEdit();
                }
            }
        }

        public void btnPlayPhrase_Click(object sender, EventArgs e)
        {
            if (this._view.ViewStatus == ViewStatusCode.PlayPhrase)
            {
                this._view.ViewStatus = ViewStatusCode.PausePhrase;
                this._aitalk.PauseAudio();
            }
            else if (this._view.ViewStatus == ViewStatusCode.PausePhrase)
            {
                this._view.ViewStatus = ViewStatusCode.PlayPhrase;
                this._aitalk.ResumeAudio();
            }
            else if (this.CheckDongleRuntime())
            {
                this._view.ViewStatus = ViewStatusCode.PlayPhrase;
                this.PrepareSynth();
                AITalkResultCode key = this._aitalk.Do(SynthMode.KanaToSpeech, this._view.PhraseKana, this.GetSynthOption(false));
                if (key != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    if (key != AITalkResultCode.AITALKERR_INVALID_ARGUMENT)
                    {
                        MessageBox.Show(this._view, "再生に失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(key), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    }
                    this._view.ViewStatus = ViewStatusCode.Edit;
                }
            }
        }

        public void btnPlayWord_Click(object sender, EventArgs e)
        {
            if (this._view.ViewStatus == ViewStatusCode.PlayWord)
            {
                this._view.ViewStatus = ViewStatusCode.PauseWord;
                this._aitalk.PauseAudio();
            }
            else if (this._view.ViewStatus == ViewStatusCode.PauseWord)
            {
                this._view.ViewStatus = ViewStatusCode.PlayWord;
                this._aitalk.ResumeAudio();
            }
            else if (this.CheckDongleRuntime())
            {
                this._view.ViewStatus = ViewStatusCode.PlayWord;
                this.PrepareSynth();
                AITalkResultCode key = this._aitalk.Do(SynthMode.KanaToSpeech, this._view.WordKana, this.GetSynthOption(false));
                if (key != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    if (key != AITalkResultCode.AITALKERR_INVALID_ARGUMENT)
                    {
                        MessageBox.Show(this._view, "再生に失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(key), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    }
                    this._view.ViewStatus = ViewStatusCode.Edit;
                }
            }
        }

        public void btnRemovePhrase_Click(object sender, EventArgs e)
        {
            this.RemovePhrase(this._view, this._view.PhraseEntry);
        }

        public void btnRemoveWord_Click(object sender, EventArgs e)
        {
            this.RemoveWord(this._view, this._view.WordEntry);
        }

        public void btnSaveKana_Click(object sender, EventArgs e)
        {
            this.SaveKanaAs();
            this._view.FocusKanaEdit();
        }

        public void btnSaveKanaFromText_Click(object sender, EventArgs e)
        {
            MessageBox.Show("未実装");
        }

        public void btnSaveWave_Click(object sender, EventArgs e)
        {
            if (this.CheckDongleRuntime() && this.CheckNGWord(this._view.SynthText))
            {
                this.SaveWave(SynthMode.TextToWave, this._view.SynthText);
                this._view.FocusMainText();
            }
        }

        public void btnSaveWaveFromKana_Click(object sender, EventArgs e)
        {
            if (this.CheckDongleRuntime())
            {
                this.SaveWave(SynthMode.Synthesize, this._view.KanaEdit);
                this._view.FocusKanaEdit();
            }
        }

        public void btnShowLog_Click(object sender, EventArgs e)
        {
            if (this._logView != null)
            {
                this._logView.Show();
                if (this._logView.WindowState == FormWindowState.Minimized)
                {
                    this._logView.WindowState = FormWindowState.Normal;
                }
                this._logView.Activate();
            }
        }

        public void btnShowPhraseList_Click(object sender, EventArgs e)
        {
            this._userDicView.ShowDialog(this._view);
        }

        public void btnShowWordList_Click(object sender, EventArgs e)
        {
            this._userDicView.ShowDialog(this._view);
        }

        public void btnStop_Click(object sender, EventArgs e)
        {
            this.StopSpeech(true);
            this._view.FocusMainText();
        }

        public void btnStopKana_Click(object sender, EventArgs e)
        {
            this.StopSpeech(false);
            this._view.FocusKanaEdit();
        }

        public void btnStopPhrase_Click(object sender, EventArgs e)
        {
            this.StopSpeech(false);
        }

        public void btnStopWord_Click(object sender, EventArgs e)
        {
            this.StopSpeech(false);
        }

        private void CalcWaveLength(SynthMode synthMode, string inputText)
        {
            if ((synthMode == SynthMode.TextToWave) || (synthMode == SynthMode.Synthesize))
            {
                this._appVariables.Progress = 0;
                this._appVariables.WaveList.Clear();
                this.PrepareSynth();
                AITalkResultCode key = this._aitalk.Do(synthMode, inputText, this.GetSynthOption(true));
                if (key != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    if (key != AITalkResultCode.AITALKERR_INVALID_ARGUMENT)
                    {
                        MessageBox.Show(this._view, "再生時間計測に失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(key), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    }
                }
                else
                {
                    if (this._appVariables.Progress < 100)
                    {
                        using (ProgressView view = new ProgressView("再生時間計測", new DoWorkEventHandler(this.CalcWaveLength_DoWork), null, synthMode == SynthMode.TextToWave, true))
                        {
                            switch (view.ShowDialog())
                            {
                                case DialogResult.Abort:
                                    this._aitalk.Abort();
                                    MessageBox.Show(view.Error.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                                    this._appVariables.Clear();
                                    return;

                                case DialogResult.Cancel:
                                    this._aitalk.Abort();
                                    MessageBox.Show("音声時間計測を中止しました。", "注意", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                                    this._appVariables.Clear();
                                    return;
                            }
                        }
                    }
                    MessageBox.Show(this._view, "再生時間は " + ((((double) CatWave(this._appVariables.WaveList).Length) / ((double) this._settingsManager.Settings.VoiceSamplePerSec))).ToString("F3") + " 秒です。", "再生時間", MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
                    this._appVariables.Clear();
                }
            }
        }

        private void CalcWaveLength_DoWork(object sender, DoWorkEventArgs e)
        {
            BackgroundWorker bw = (BackgroundWorker) sender;
            this.ShowProgress(bw, e, "再生時間を計測しています。");
            bw.ReportProgress(100, "再生時間を計測しています。");
            Thread.Sleep(200);
        }

        public static short[] CatWave(List<short[]> waveList)
        {
            int num = 0;
            foreach (short[] numArray in waveList)
            {
                num += numArray.Length;
            }
            short[] dst = new short[num];
            int dstOffset = 0;
            foreach (short[] numArray3 in waveList)
            {
                Buffer.BlockCopy(numArray3, 0, dst, dstOffset, numArray3.Length * 2);
                dstOffset += numArray3.Length * 2;
            }
            return dst;
        }

        private bool CheckDongleRuntime()
        {
            if (this._dongleAuth != null)
            {
                try
                {
                    this._dongleAuth.Login(0);
                }
                catch (Exception exception)
                {
                    MessageBox.Show(this._view, "USBキーの認証に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    return false;
                }
            }
            return true;
        }

        public bool CheckIgnoredVoiceName(string voiceName, List<string> ignoredVoiceNames)
        {
            bool flag = false;
            if (ignoredVoiceNames != null)
            {
                foreach (string str in ignoredVoiceNames)
                {
                    if (str == voiceName)
                    {
                        flag = true;
                    }
                }
            }
            return flag;
        }

        private bool CheckNGWord(string text)
        {
            if (this._appSettings.NGWord.Enabled)
            {
                string input = Strings.StrConv(text, VbStrConv.Wide, 0);
                string str2 = "";
                foreach (string str3 in this._appSettings.NGWord.Items.Keys)
                {
                    if (Regex.IsMatch(input, str3))
                    {
                        str2 = str2 + "【" + str3 + "】 ";
                    }
                }
                if (str2 != "")
                {
                    MessageBox.Show(this._view, this._appSettings.NGWord.Message + Environment.NewLine + Environment.NewLine + str2, "注意", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                    return false;
                }
            }
            return true;
        }

        private void CreateDefaultUserDic(Form owner)
        {
            if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.PhraseDicSupport))
            {
                try
                {
                    if (!Directory.Exists(this._appSettings.UserDic.DefaultPhraseDicDirPath))
                    {
                        Directory.CreateDirectory(this._appSettings.UserDic.DefaultPhraseDicDirPath);
                    }
                    if (!File.Exists(this._appSettings.UserDic.DefaultPhraseDicFilePath))
                    {
                        new PhraseDic().Write(this._appSettings.UserDic.DefaultPhraseDicFilePath);
                    }
                }
                catch
                {
                    Common.MessageBox.Show(owner, "フレーズ辞書の作成に失敗しました。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
                }
            }
            if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.WordDicSupport))
            {
                try
                {
                    if (!Directory.Exists(this._appSettings.UserDic.DefaultWordDicDirPath))
                    {
                        Directory.CreateDirectory(this._appSettings.UserDic.DefaultWordDicDirPath);
                    }
                    if (!File.Exists(this._appSettings.UserDic.DefaultWordDicFilePath))
                    {
                        new WordDic().Write(this._appSettings.UserDic.DefaultWordDicFilePath);
                    }
                }
                catch
                {
                    Common.MessageBox.Show(owner, "単語辞書の作成に失敗しました。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
                }
            }
            if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.SymbolDicSupport))
            {
                try
                {
                    if (!Directory.Exists(this._appSettings.UserDic.DefaultSymbolDicDirPath))
                    {
                        Directory.CreateDirectory(this._appSettings.UserDic.DefaultSymbolDicDirPath);
                    }
                    if (!File.Exists(this._appSettings.UserDic.DefaultSymbolDicFilePath))
                    {
                        new SymbolDic().Write(this._appSettings.UserDic.DefaultSymbolDicFilePath);
                    }
                }
                catch
                {
                    Common.MessageBox.Show(owner, "記号ポーズ辞書の作成に失敗しました。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
                }
            }
        }

        public List<VoiceInfo> EnumVoiceNames(string dbsPath, int voiceSamplePerSec)
        {
            List<VoiceInfo> list = new List<VoiceInfo>();
            string searchPattern = (voiceSamplePerSec == 0x3e80) ? "*16" : "*22";
            try
            {
                foreach (string str2 in Directory.GetDirectories(dbsPath, searchPattern))
                {
                    string fileName = Path.GetFileName(str2);
                    if (this.IsVoiceDic(str2))
                    {
                        VoiceInfo item = new VoiceInfo(fileName);
                        try
                        {
                            item.ReadVoiceInfo(Path.Combine(str2, Common.VoiceInfoFileName));
                        }
                        catch
                        {
                        }
                        list.Add(item);
                    }
                }
            }
            catch (DirectoryNotFoundException)
            {
            }
            return list;
        }

        private void GenerateKana()
        {
            this._appVariables.Progress = 0;
            this._appVariables.SynthText = this._view.SynthText;
            this._appVariables.KanaList.Clear();
            this.PrepareSynth();
            AITalkResultCode key = this._aitalk.Do(SynthMode.TextProcess, this._view.SynthText, this.GetSynthOption(false));
            if (key != AITalkResultCode.AITALKERR_SUCCESS)
            {
                if (key != AITalkResultCode.AITALKERR_INVALID_ARGUMENT)
                {
                    MessageBox.Show(this._view, "中間言語作成に失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(key), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                }
            }
            else
            {
                if (this._appVariables.Progress < 100)
                {
                    using (ProgressView view = new ProgressView("中間言語作成", new DoWorkEventHandler(this.GenerateKana_DoWork), null, true, true))
                    {
                        switch (view.ShowDialog())
                        {
                            case DialogResult.Abort:
                                this._aitalk.Abort();
                                MessageBox.Show(view.Error.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                                this._appVariables.Clear();
                                return;

                            case DialogResult.Cancel:
                                this._aitalk.Abort();
                                MessageBox.Show("中間言語作成を中止しました。", "注意", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                                this._appVariables.Clear();
                                return;
                        }
                    }
                }
                string str = "";
                foreach (string str2 in this._appVariables.KanaList)
                {
                    str = str + str2;
                }
                this._view.KanaEdit = str;
                this._view.SelectedTuningTab = TuningTab.KanaEdit;
                this._appVariables.Clear();
            }
        }

        private void GenerateKana_DoWork(object sender, DoWorkEventArgs e)
        {
            BackgroundWorker worker = (BackgroundWorker) sender;
            do
            {
                worker.ReportProgress(this._appVariables.Progress, "中間言語を作成しています。");
                Thread.Sleep(100);
            }
            while (this._appVariables.Progress < 100);
            worker.ReportProgress(100, "中間言語を作成しています。");
            Thread.Sleep(200);
        }

        [DllImport("user32.dll")]
        public static extern IntPtr GetDesktopWindow();
        private SynthOption GetSynthOption(bool useBeginTermPause)
        {
            SynthOption none = SynthOption.None;
            if (useBeginTermPause)
            {
                none |= SynthOption.UseBeginTermPause;
            }
            if (!this._settingsManager.Settings.HandleNewLineAsSentenceEnd)
            {
                none |= SynthOption.IgnoreNewLine;
            }
            return none;
        }

        public static string GetTextFilePathFromWaveFilePath(string waveFilePath)
        {
            return Path.Combine(Path.GetDirectoryName(waveFilePath), Path.GetFileNameWithoutExtension(waveFilePath) + ".txt");
        }

        private void ImportSettings()
        {
            using (ProgressView view = new ProgressView("設定のインポート", new DoWorkEventHandler(this.InitializeView_DoWork), null, true, false))
            {
                DialogResult result = view.ShowDialog();
                if (result == DialogResult.Abort)
                {
                    MessageBox.Show(view.Error.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                }
            }
            this._userDicView.UpdateUserSettings(this._settingsManager.Settings);
            this._view.UpdateUserSettings(this._settingsManager.Settings, this._symbolDic);
        }

        private void Initialize()
        {
            using (InitializeView view = new InitializeView(this._appSettings, new DoWorkEventHandler(this.InitializeView_DoWork), null))
            {
                DialogResult result = view.ShowDialog();
                if (result == DialogResult.Abort)
                {
                    Exception error = view.Error;
                    MessageBox.Show(view, error.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                }
            }
            base.MainForm = this._view;
            this._userDicView.UpdateUserSettings(this._settingsManager.Settings);
            this._view.UpdateUserSettings(this._settingsManager.Settings, this._symbolDic);
            this._view.Show();
        }

        private void InitializeAITalk(bool reset, BackgroundWorker bw, int beginPercentage = 0)
        {
            if (bw != null)
            {
                bw.ReportProgress(beginPercentage, "音声合成エンジンを初期化しています。");
            }
            this._appVariables.Status = AppStatus.None;
            if (reset)
            {
                this._aitalk.End();
            }
            AITalk_TConfig config = new AITalk_TConfig {
                dirVoiceDBS = this._settingsManager.Settings.DbsPath,
                hzVoiceDB = this._settingsManager.Settings.VoiceSamplePerSec,
                msecTimeout = this._appSettings.Timeout,
                pathLicense = Path.Combine(Application.StartupPath, this._appSettings.LicenseFileName),
                codeAuthSeed = this._appSettings.AuthCode,
                lenAuthSeed = 0
            };
            AITalkResultCode key = this._aitalk.Init(config);
            switch (key)
            {
                case AITalkResultCode.AITALKERR_SUCCESS:
                case AITalkResultCode.AITALKERR_ALREADY_INITIALIZED:
                    this._appVariables.Status |= AppStatus.AITalkInitialized;
                    return;
            }
            if (!File.Exists(config.pathLicense))
            {
                throw new Exception("音声合成エンジンの初期化に失敗しました。" + Environment.NewLine + "ライセンスファイルが存在しません。");
            }
            if (!Directory.Exists(config.dirVoiceDBS))
            {
                throw new Exception("音声合成エンジンの初期化に失敗しました。" + Environment.NewLine + "音声辞書フォルダ " + config.dirVoiceDBS + " は存在しません。");
            }
            throw new Exception("音声合成エンジンの初期化に失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(key));
        }

        private void InitializeAppMode()
        {
            string str2;
            string str3;
            string str4;
            string str5;
            string str6;
            string str7;
            AITalk_TConfig config = new AITalk_TConfig {
                dirVoiceDBS = Application.StartupPath,
                hzVoiceDB = this._settingsManager.Settings.VoiceSamplePerSec,
                msecTimeout = this._appSettings.Timeout,
                pathLicense = Path.Combine(Application.StartupPath, this._appSettings.LicenseFileName),
                codeAuthSeed = "",
                lenAuthSeed = 0
            };
            if (!File.Exists(config.pathLicense))
            {
                MessageBox.Show("ライセンス認証に失敗しました。" + Environment.NewLine + "ライセンスファイルが存在しません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                throw new InitializeException();
            }
            if (this._appSettings.AuthCodeFixed)
            {
                config.codeAuthSeed = this._appSettings.AuthCode;
                AITalkResultCode key = this._aitalk.Init(config);
                if (key != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    MessageBox.Show("ライセンス認証に失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(key), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    throw new InitializeException();
                }
                goto Label_024E;
            }
            try
            {
                string str = (string) Registry.GetValue(this._appSettings.LicenseKeyRegistryKeyPath, this._appSettings.LicenseKeyRegistryValueName, "");
                this._appSettings.AuthCode = (str != null) ? str : "";
            }
            catch (Exception exception)
            {
                MessageBox.Show("ライセンスキーの取得に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
            }
            bool flag = false;
        Label_0165:
            if (this._appSettings.AuthCode != "")
            {
                config.codeAuthSeed = this._appSettings.AuthCode;
                AITalkResultCode code2 = this._aitalk.Init(config);
                if (code2 == AITalkResultCode.AITALKERR_SUCCESS)
                {
                    goto Label_020F;
                }
                MessageBox.Show("ライセンス認証に失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(code2), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                if (code2 != AITalkResultCode.AITALKERR_LICENSE_ABSENT)
                {
                    throw new InitializeException();
                }
            }
            using (LicenseKeyView view = new LicenseKeyView())
            {
                if (view.ShowDialog() != DialogResult.OK)
                {
                    throw new InitializeException();
                }
                this._appSettings.AuthCode = view.LicenseKey;
                flag = true;
                goto Label_0165;
            }
        Label_020F:
            if (flag)
            {
                try
                {
                    this.WriteLicenseKey(this._appSettings.AuthCode);
                }
                catch (Exception exception2)
                {
                    MessageBox.Show("ライセンスキーの保存に失敗しました。" + Environment.NewLine + exception2.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                }
            }
        Label_024E:
            if ((AITalkEditorAPI.GetLicenseInfo("EDITION", out str2, 0x400) != AITalkResultCode.AITALKERR_SUCCESS) || (this._appSettings.Edition != str2))
            {
                MessageBox.Show("ライセンス認証に失敗しました。" + Environment.NewLine + "本製品のライセンス情報がありません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                throw new InitializeException();
            }
            if ((AITalkEditorAPI.GetLicenseInfo("USEDONGLE", out str3, 0x400) != AITalkResultCode.AITALKERR_SUCCESS) || (str3 != "NO"))
            {
                if (!File.Exists(Path.Combine(Application.StartupPath, "hasp_net_windows.dll")) || !File.Exists(Path.Combine(Application.StartupPath, "hasp_windows_91672.dll")))
                {
                    MessageBox.Show("ライセンス認証に失敗しました。" + Environment.NewLine + "認証に必要なライブラリが見つかりません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    throw new InitializeException();
                }
                try
                {
                    this._dongleAuth = new DongleAuth();
                    this._dongleAuth.Login(this._appSettings.FeatureID);
                }
                catch (Exception exception3)
                {
                    MessageBox.Show("USBキーの認証に失敗しました。" + Environment.NewLine + exception3.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    throw new InitializeException();
                }
            }
            if ((AITalkEditorAPI.GetLicenseInfo("LANGTYPE", out str4, 0x400) != AITalkResultCode.AITALKERR_SUCCESS) || ((str4 != "STANDARD") && (str4 != "MICRO")))
            {
                MessageBox.Show("ライセンス認証に失敗しました。" + Environment.NewLine + "日本語解析機能のライセンスがありません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                throw new InitializeException();
            }
            if (((AITalkEditorAPI.ModuleFlag() & 2) == 0) && (str4 != "STANDARD"))
            {
                MessageBox.Show("ライセンス認証に失敗しました。" + Environment.NewLine + "標準版日本語解析機能のライセンスがありません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                throw new InitializeException();
            }
            if (((AITalkEditorAPI.ModuleFlag() & 2) == 2) && (str4 != "MICRO"))
            {
                MessageBox.Show("ライセンス認証に失敗しました。" + Environment.NewLine + "圧縮版日本語解析機能のライセンスがありません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                throw new InitializeException();
            }
            if ((AITalkEditorAPI.GetLicenseInfo("VOICETYPE", out str5, 0x400) != AITalkResultCode.AITALKERR_SUCCESS) || ((str5 != "STANDARD") && (str5 != "MICRO")))
            {
                MessageBox.Show("ライセンス認証に失敗しました。" + Environment.NewLine + "音声合成機能のライセンスがありません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                throw new InitializeException();
            }
            if (((AITalkEditorAPI.ModuleFlag() & 1) == 0) && (str5 != "STANDARD"))
            {
                MessageBox.Show("ライセンス認証に失敗しました。" + Environment.NewLine + "標準版音声合成機能のライセンスがありません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                throw new InitializeException();
            }
            if (((AITalkEditorAPI.ModuleFlag() & 1) == 1) && (str5 != "MICRO"))
            {
                MessageBox.Show("ライセンス認証に失敗しました。" + Environment.NewLine + "圧縮版音声合成機能のライセンスがありません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                throw new InitializeException();
            }
            if ((AITalkEditorAPI.GetLicenseInfo("SAVEWAVE", out str6, 0x400) != AITalkResultCode.AITALKERR_SUCCESS) || ((str6 != "ENABLED") && (str6 != "DISABLED")))
            {
                this._appSettings.AppMode &= ~AppMode.SaveWaveSupport;
            }
            else if (str6 == "DISABLED")
            {
                this._appSettings.AppMode &= ~AppMode.SaveWaveEnabled;
            }
            if ((AITalkEditorAPI.GetLicenseInfo("SAVEKANA", out str7, 0x400) != AITalkResultCode.AITALKERR_SUCCESS) || ((str7 != "ENABLED") && (str7 != "DISABLED")))
            {
                this._appSettings.AppMode &= ~AppMode.KanaSupport;
            }
            else if (str7 == "DISABLED")
            {
                this._appSettings.AppMode &= ~AppMode.KanaSupport;
            }
        }

        private void InitializeAudio(bool reset, Form parent, BackgroundWorker bw, int beginPercentage = 0)
        {
            if (bw != null)
            {
                bw.ReportProgress(beginPercentage, "音声デバイスを初期化しています。");
            }
            this._appVariables.Status &= ~AppStatus.AudioInitialized;
            if (reset)
            {
                this._aitalk.CloseAudio();
            }
            AIAudio_TConfig param = new AIAudio_TConfig {
                msecLatency = this._appSettings.SoundBufferLatency,
                lenBufferBytes = (uint) ((this._settingsManager.Settings.VoiceSamplePerSec * 2) * this._appSettings.SoundBufferLength),
                hzSamplesPerSec = this._settingsManager.Settings.SoundOutput.SamplePerSec,
                formatTag = this._settingsManager.Settings.SoundOutput.DataFormat
            };
            AIAudioResultCode key = this._aitalk.OpenAudio(ref param);
            switch (key)
            {
                case AIAudioResultCode.AIAUDIOERR_SUCCESS:
                case AIAudioResultCode.AIAUDIOERR_ALREADY_OPENED:
                    this._appVariables.Status |= AppStatus.AudioInitialized;
                    return;
            }
            Common.MessageBox.Show(parent, "音声デバイスの初期化に失敗しました。" + Environment.NewLine + AIAudioErrorMessage.GetErrorMessage(key), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
        }

        private void InitializeLangDic(bool reset, Form parent, BackgroundWorker bw, int beginPercentage = 0, int endPercentage = 100)
        {
            if (bw != null)
            {
                bw.ReportProgress(beginPercentage, "日本語標準辞書をロードしています。");
            }
            int num = (endPercentage - beginPercentage) / 4;
            this._appVariables.Status &= ~AppStatus.LandLoaded;
            this._appVariables.Status &= ~AppStatus.PhraseDicEditable;
            this._appVariables.Status &= ~AppStatus.WordDicEditable;
            this._appVariables.Status &= ~AppStatus.SymbolDicEditable;
            if (reset || AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.MicroLang))
            {
                this._aitalk.LangClear();
            }
            this.CreateDefaultUserDic(parent);
            string text = this.PrepareMicroWordDic();
            AITalkResultCode key = this._aitalk.LangLoad(this._settingsManager.Settings.LangPath);
            switch (key)
            {
                case AITalkResultCode.AITALKERR_SUCCESS:
                case AITalkResultCode.AITALKERR_ALREADY_LOADED:
                    this._appVariables.Status |= AppStatus.LandLoaded;
                    if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.PhraseDicSupport))
                    {
                        if (bw != null)
                        {
                            bw.ReportProgress(beginPercentage + num, "フレーズ辞書をロードしています。");
                        }
                        try
                        {
                            if (this._settingsManager.Settings.UserDic.PhraseDicEnabled)
                            {
                                try
                                {
                                    this._phraseDic.StartUpdate();
                                    this._phraseDic.Read(this._settingsManager.Settings.UserDic.PhraseDicPath);
                                    this._phraseDic.EndUpdate();
                                    this._phraseDic.PageIndex = 0;
                                    this._appVariables.Status |= AppStatus.PhraseDicEditable;
                                    goto Label_022B;
                                }
                                catch (Exception exception)
                                {
                                    throw new Exception("フレーズ辞書のロードに失敗しました。" + Environment.NewLine + exception.Message);
                                }
                            }
                            this._phraseDic.Clear();
                        Label_022B:
                            this.ReloadPhraseDic();
                        }
                        catch (Exception exception2)
                        {
                            Common.MessageBox.Show(parent, exception2.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
                        }
                    }
                    if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.WordDicSupport))
                    {
                        if (bw != null)
                        {
                            bw.ReportProgress(beginPercentage + (num * 2), "単語辞書をロードしています。");
                        }
                        try
                        {
                            if (this._settingsManager.Settings.UserDic.WordDicEnabled)
                            {
                                try
                                {
                                    this._wordDic.StartUpdate();
                                    this._wordDic.Read(this._settingsManager.Settings.UserDic.WordDicPath);
                                    this._wordDic.EndUpdate();
                                    this._wordDic.PageIndex = 0;
                                    this._appVariables.Status |= AppStatus.WordDicEditable;
                                    goto Label_0310;
                                }
                                catch (Exception exception3)
                                {
                                    throw new Exception("単語辞書のロードに失敗しました。" + Environment.NewLine + exception3.Message);
                                }
                            }
                            this._wordDic.Clear();
                        Label_0310:
                            this.ReloadWordDic();
                            if (text != "")
                            {
                                Common.MessageBox.Show(parent, text, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
                            }
                        }
                        catch (Exception exception4)
                        {
                            Common.MessageBox.Show(parent, exception4.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
                        }
                    }
                    if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.SymbolDicSupport))
                    {
                        if (bw != null)
                        {
                            bw.ReportProgress(beginPercentage + (num * 3), "記号ポーズ辞書をロードしています。");
                        }
                        try
                        {
                            if (this._settingsManager.Settings.UserDic.SymbolDicEnabled)
                            {
                                try
                                {
                                    this._symbolDic.StartUpdate();
                                    this._symbolDic.Read(this._settingsManager.Settings.UserDic.SymbolDicPath);
                                    this._symbolDic.EndUpdate();
                                    this._symbolDic.PageIndex = 0;
                                    this._appVariables.Status |= AppStatus.SymbolDicEditable;
                                    goto Label_0414;
                                }
                                catch (Exception exception5)
                                {
                                    throw new Exception("記号ポーズ辞書のロードに失敗しました。" + Environment.NewLine + exception5.Message);
                                }
                            }
                            this._symbolDic.Clear();
                        Label_0414:
                            this.ReloadSymbolDic();
                        }
                        catch (Exception exception6)
                        {
                            Common.MessageBox.Show(parent, exception6.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
                        }
                    }
                    return;
            }
            if (!Directory.Exists(this._settingsManager.Settings.LangPath))
            {
                Common.MessageBox.Show(parent, "日本語辞書のロードに失敗しました。" + Environment.NewLine + "日本語辞書フォルダ " + this._settingsManager.Settings.LangPath + " は存在しません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
            }
            else
            {
                Common.MessageBox.Show(parent, "日本語辞書のロードに失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(key), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
            }
        }

        private void InitializeView_DoWork(object sender, DoWorkEventArgs e)
        {
            BackgroundWorker bw = (BackgroundWorker) sender;
            Form parent = ((DoWorkEventArgsEx) e.Argument).Parent;
            this.InitializeAITalk(true, null, 0);
            this.InitializeAudio(false, parent, bw, 10);
            this.InitializeLangDic(false, parent, bw, 30, 50);
            this.InitializeVoiceDic(parent, bw, 50, 100);
            bw.ReportProgress(100, "起動の準備をしています。");
            Thread.Sleep(200);
        }

        private void InitializeVoiceDic(Form parent, BackgroundWorker bw, int beginPercentage = 0, int endPercentage = 100)
        {
            this._appVariables.LoadedVoices.Clear();
            List<VoiceInfo> list = this.EnumVoiceNames(this._settingsManager.Settings.DbsPath, this._settingsManager.Settings.VoiceSamplePerSec);
            List<VoiceInfo> list2 = new List<VoiceInfo>();
            List<string> ignoredVoiceNames = this._settingsManager.Settings.IgnoredVoiceNames;
            foreach (VoiceInfo info in list)
            {
                if (!this.CheckIgnoredVoiceName(info.DirectoryName, ignoredVoiceNames))
                {
                    list2.Add(info);
                }
            }
            if (list2.Count != 0)
            {
                int num = (endPercentage - beginPercentage) / list2.Count;
                int percentProgress = beginPercentage;
                foreach (VoiceInfo info2 in list2)
                {
                    if (bw != null)
                    {
                        bw.ReportProgress(percentProgress, "音声辞書 " + info2.DirectoryName + " をロードしています。");
                    }
                    AITalkResultCode key = this._aitalk.VoiceLoad(info2.DirectoryName);
                    switch (key)
                    {
                        case AITalkResultCode.AITALKERR_SUCCESS:
                        case AITalkResultCode.AITALKERR_ALREADY_LOADED:
                            this._appVariables.LoadedVoices.Add(info2);
                            this._appVariables.Status |= AppStatus.VoiceLoaded;
                            break;

                        default:
                            Common.MessageBox.Show(parent, "音声辞書 " + info2.DirectoryName + " のロードに失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(key), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
                            break;
                    }
                    percentProgress += num;
                }
            }
        }

        private bool IsVoiceDic(string voicePath)
        {
            string[] voiceDicRequiredFilesStandard;
            if (!AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.MicroVoice))
            {
                voiceDicRequiredFilesStandard = Common.VoiceDicRequiredFilesStandard;
            }
            else
            {
                voiceDicRequiredFilesStandard = Common.VoiceDicRequiredFilesMicro;
            }
            foreach (string str in voiceDicRequiredFilesStandard)
            {
                if (!File.Exists(Path.Combine(voicePath, str)))
                {
                    return false;
                }
            }
            return true;
        }

        public void MainView_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (((this._view.MainTextModified || this._view.KanaEditModified) || (this._view.PhraseChanged || this._view.WordChanged)) && (DialogResult.Yes != MessageBox.Show(this._view, "編集中の内容があります。" + Environment.NewLine + "プログラムを終了してよろしいですか？", "注意", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2)))
            {
                e.Cancel = true;
            }
            else
            {
                this.StopSpeech(false);
                try
                {
                    this.UpdateSoundEffectSetting();
                }
                catch
                {
                    MessageBox.Show(this._view, "設定の保存に失敗しました。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                }
            }
        }

        private void OnErrorOccured(object sender, AITalkUtilEx.ErrorEventArgs e)
        {
            MessageBox.Show(string.Concat(new object[] { "合成処理中にエラーが発生しました。", Environment.NewLine, "エラー名 : ", e.Name, Environment.NewLine, "エラータイプ : ", e.Type, Environment.NewLine, "エラーコード : ", (e.Type == AITalkUtilEx.ErrorType.AITalk) ? ((AITalkResultCode) e.ErrorCode).ToString() : ((AIAudioResultCode) e.ErrorCode).ToString() }), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
        }

        private void OnPlayBookmark(object sender, AITalkUtilEx.AudioEventArgs e)
        {
            if (((this._aitalk.SynthMode == SynthMode.TextToSpeech) && (e.Text != "")) && AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.HighlightSupport))
            {
                this._view.HighlightNext(e.Pos, e.Text, e.Kana);
            }
        }

        private void OnPlayComplete(object sender, AITalkUtilEx.AudioEventArgs e)
        {
            this._view.HighlightTeardown(true);
            this._view.ViewStatus = ViewStatusCode.Edit;
        }

        private void OnPlayPhonemeLabel(object sender, AITalkUtilEx.PhonemeLabelEventArgs e)
        {
            if ((this._aitalk.SynthMode & SynthMode.Play) == SynthMode.Play)
            {
                this._view.LipSync(e.Tick, e.Label);
            }
        }

        private void OnPlaySentence(object sender, AITalkUtilEx.AudioEventArgs e)
        {
            if ((this._aitalk.SynthMode == SynthMode.TextToSpeech) && (e.Text != ""))
            {
                if (!AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.HighlightSupport))
                {
                    this._view.HighlightNext(e.Pos, e.Text, e.Kana);
                }
                this._view.UpdatePhraseEdit(e.Text, e.Kana);
            }
        }

        private void OnSynthesizingComplete(object sender, AITalkUtilEx.SynthesizingEventArgs e)
        {
            if ((this._aitalk.SynthMode == SynthMode.TextToWave) || (this._aitalk.SynthMode == SynthMode.Synthesize))
            {
                this._appVariables.Progress = e.Progress;
                if (e.Wave != null)
                {
                    this._appVariables.WaveList.Add(e.Wave);
                }
            }
        }

        private void OnSynthesizingProgress(object sender, AITalkUtilEx.SynthesizingEventArgs e)
        {
            if ((this._aitalk.SynthMode == SynthMode.TextToWave) || (this._aitalk.SynthMode == SynthMode.Synthesize))
            {
                this._appVariables.Progress = e.Progress;
                if (e.Wave != null)
                {
                    this._appVariables.WaveList.Add(e.Wave);
                }
            }
        }

        private void OnTextProcessingComplete(object sender, AITalkUtilEx.TextProcessingEventArgs e)
        {
            if (this._aitalk.SynthMode == SynthMode.TextProcess)
            {
                this._appVariables.Progress = e.Progress;
                this._appVariables.KanaList.Add(e.Kana);
            }
        }

        private void OnTextProcessingProgress(object sender, AITalkUtilEx.TextProcessingEventArgs e)
        {
            if (this._aitalk.SynthMode == SynthMode.TextProcess)
            {
                this._appVariables.Progress = e.Progress;
                this._appVariables.KanaList.Add(e.Kana);
            }
        }

        private void OnWriteLog(object sender, AITalkUtil.LogEventArgs e)
        {
            if (this._logView != null)
            {
                this._logView.WriteLine(e.Text);
            }
            if ((this._appSettings.LogOutput & AppSettings.LogOutoutMode.File) == AppSettings.LogOutoutMode.File)
            {
                this.WriteLogOnFile(e.Text);
            }
        }

        private void OpenKana(string fileName)
        {
            try
            {
                using (StreamReader reader = new StreamReader(fileName, Encoding.GetEncoding("Shift_JIS")))
                {
                    this._view.KanaEdit = reader.ReadToEnd();
                }
            }
            catch (Exception exception)
            {
                MessageBox.Show(this._view, "中間言語の読み込みに失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
            }
            this._settingsManager.Settings.KanaDirectoryPath = Path.GetDirectoryName(fileName);
            this._view.KanaEditModified = false;
            this._view.SelectedTuningTab = TuningTab.KanaEdit;
        }

        private void OpenText(string fileName)
        {
            try
            {
                using (StreamReader reader = new StreamReader(fileName, Encoding.GetEncoding("Shift_JIS")))
                {
                    this._view.MainText = reader.ReadToEnd();
                }
            }
            catch (Exception exception)
            {
                MessageBox.Show(this._view, "テキストの読み込みに失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
            }
            this._settingsManager.Settings.TextDirectoryPath = Path.GetDirectoryName(fileName);
            this._appVariables.TextFilePath = fileName;
            this._view.TextFileName = Path.GetFileName(fileName);
            this._view.MainTextModified = false;
        }

        private string PrepareMicroWordDic()
        {
            if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.MicroLang))
            {
                string destFileName = Path.Combine(this._settingsManager.Settings.LangPath, Common.MicroWordDicFilePath);
                if (this._settingsManager.Settings.UserDic.WordDicEnabled)
                {
                    try
                    {
                        File.Copy(this._settingsManager.Settings.UserDic.WordDicPath, destFileName, true);
                        goto Label_00AA;
                    }
                    catch (Exception exception)
                    {
                        return ("単語辞書のロードに失敗しました。" + exception.Message);
                    }
                }
                try
                {
                    using (File.Create(destFileName))
                    {
                    }
                }
                catch (Exception exception2)
                {
                    return ("単語辞書のアンロードに失敗しました。" + exception2.Message);
                }
            }
        Label_00AA:
            return "";
        }

        public void PreparePhrase(PhraseEntry phraseEntry)
        {
            if (phraseEntry != null)
            {
                this._view.PhraseEntry = phraseEntry;
            }
        }

        private void PrepareSynth()
        {
            this.UpdateSoundEffectSetting();
            if (this.SetSettings(this._settingsManager.Settings) != AITalkResultCode.AITALKERR_SUCCESS)
            {
                MessageBox.Show(this._view, "音声合成に使用するパラメータの設定に失敗しました。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
            }
        }

        public void PrepareWord(WordEntry wordEntry)
        {
            if (wordEntry != null)
            {
                this._view.WordEntry = wordEntry;
            }
        }

        private void ReloadPhraseDic()
        {
            if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.PhraseDicSupport))
            {
                if (this._settingsManager.Settings.UserDic.PhraseDicEnabled && (this._phraseDic.Count > 0))
                {
                    if (this._aitalk.ReloadPhraseDic(this._settingsManager.Settings.UserDic.PhraseDicPath) != AITalkResultCode.AITALKERR_SUCCESS)
                    {
                        throw new Exception("フレーズ辞書のロードに失敗しました。");
                    }
                }
                else if (this._aitalk.ReloadPhraseDic(null) != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    throw new Exception("フレーズ辞書のアンロードに失敗しました。");
                }
            }
        }

        private void ReloadSymbolDic()
        {
            if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.SymbolDicSupport))
            {
                if (this._settingsManager.Settings.UserDic.SymbolDicEnabled && (this._symbolDic.Count > 0))
                {
                    if (this._aitalk.ReloadSymbolDic(this._settingsManager.Settings.UserDic.SymbolDicPath) != AITalkResultCode.AITALKERR_SUCCESS)
                    {
                        throw new Exception("記号ポーズ辞書のロードに失敗しました。");
                    }
                }
                else if (this._aitalk.ReloadSymbolDic(null) != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    throw new Exception("記号ポーズ辞書のアンロードに失敗しました。");
                }
            }
        }

        private void ReloadWordDic()
        {
            if (!AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.MicroLang) && AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.WordDicSupport))
            {
                if (this._settingsManager.Settings.UserDic.WordDicEnabled && (this._wordDic.Count > 0))
                {
                    if (this._aitalk.ReloadWordDic(this._settingsManager.Settings.UserDic.WordDicPath) != AITalkResultCode.AITALKERR_SUCCESS)
                    {
                        throw new Exception("単語辞書のロードに失敗しました。");
                    }
                }
                else if (this._aitalk.ReloadWordDic(null) != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    throw new Exception("単語辞書のアンロードに失敗しました。");
                }
            }
        }

        public void RemovePhrase(IWin32Window owner, PhraseEntry phraseEntry)
        {
            if (phraseEntry != null)
            {
                this._phraseDic.StartUpdate();
                int index = this._phraseDic.CheckExistence(phraseEntry);
                if (index == -1)
                {
                    MessageBox.Show(owner, "フレーズが登録されていません。", "注意", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                    this._phraseDic.EndUpdate();
                }
                else if (DialogResult.Yes != MessageBox.Show(owner, "フレーズを削除してよろしいですか？", "確認", MessageBoxButtons.YesNo, MessageBoxIcon.Asterisk, MessageBoxDefaultButton.Button2))
                {
                    this._phraseDic.EndUpdate();
                }
                else
                {
                    try
                    {
                        this._phraseDic.RemoveAt(index);
                    }
                    catch (Exception exception)
                    {
                        MessageBox.Show(owner, "フレーズの削除に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                        this._phraseDic.EndUpdate();
                        return;
                    }
                    try
                    {
                        this._phraseDic.Write(this._settingsManager.Settings.UserDic.PhraseDicPath);
                    }
                    catch (Exception exception2)
                    {
                        MessageBox.Show(owner, "フレーズ辞書の書き込みに失敗しました。" + Environment.NewLine + exception2.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                        this._phraseDic.EndUpdate();
                        return;
                    }
                    this._phraseDic.EndUpdate();
                    try
                    {
                        this.ReloadPhraseDic();
                    }
                    catch (Exception exception3)
                    {
                        MessageBox.Show(this._view, exception3.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                        return;
                    }
                    MessageBox.Show(owner, "フレーズを削除しました。", "情報", MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
                }
            }
        }

        public void RemoveWord(IWin32Window owner, WordEntry wordEntry)
        {
            if (wordEntry != null)
            {
                this._wordDic.StartUpdate();
                int index = this._wordDic.CheckExistence(wordEntry);
                if (index == -1)
                {
                    MessageBox.Show(owner, "単語が登録されていません。", "注意", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                    this._wordDic.EndUpdate();
                }
                else if (DialogResult.Yes != MessageBox.Show(owner, "単語を削除してよろしいですか？", "確認", MessageBoxButtons.YesNo, MessageBoxIcon.Asterisk, MessageBoxDefaultButton.Button2))
                {
                    this._wordDic.EndUpdate();
                }
                else
                {
                    try
                    {
                        this._wordDic.RemoveAt(index);
                    }
                    catch (Exception exception)
                    {
                        MessageBox.Show(owner, "単語の削除に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                        this._wordDic.EndUpdate();
                        return;
                    }
                    try
                    {
                        this._wordDic.Write(this._settingsManager.Settings.UserDic.WordDicPath);
                    }
                    catch (Exception exception2)
                    {
                        MessageBox.Show(owner, "単語辞書の書き込みに失敗しました。" + Environment.NewLine + exception2.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                        this._wordDic.EndUpdate();
                        return;
                    }
                    this._wordDic.EndUpdate();
                    if (AppModeUtil.CheckSupport(this._appSettings.AppMode, AppMode.MicroLang))
                    {
                        this.InitializeLangDic(true, this._view, null, 0, 100);
                    }
                    else
                    {
                        try
                        {
                            this.ReloadWordDic();
                        }
                        catch (Exception exception3)
                        {
                            MessageBox.Show(this._view, exception3.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                            return;
                        }
                    }
                    MessageBox.Show(owner, "単語を削除しました。", "情報", MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
                }
            }
        }

        public static void Run(AppSettings appSettings)
        {
            SingleInstance instance = new SingleInstance(appSettings.Title);
            if (!instance.Lock())
            {
                if (!instance.ActivateWindow())
                {
                    MessageBox.Show("既に実行しています。", "注意", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                }
            }
            else
            {
                try
                {
                    Application.Run(new MainPresenter(appSettings));
                }
                catch (InitializeException)
                {
                }
                instance.Unlock();
            }
        }

        private void SaveKana(string fileName)
        {
            try
            {
                using (StreamWriter writer = new StreamWriter(fileName, false, Encoding.GetEncoding("Shift_JIS")))
                {
                    writer.Write(Common.ReplaceNewLine(this._view.KanaEdit));
                }
            }
            catch (Exception exception)
            {
                MessageBox.Show(this._view, "中間言語の保存に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
            }
            this._view.KanaEditModified = false;
        }

        private void SaveKanaAs()
        {
            using (SaveFileDialog dialog = new SaveFileDialog())
            {
                string kanaFileExtension = Common.KanaFileExtension;
                dialog.CheckPathExists = true;
                dialog.DefaultExt = kanaFileExtension;
                dialog.FileName = "";
                dialog.Filter = "中間言語ファイル (*." + kanaFileExtension + ")|*." + kanaFileExtension + "|すべてのファイル (*.*)|*.*";
                dialog.InitialDirectory = this._settingsManager.Settings.KanaDirectoryPath;
                dialog.RestoreDirectory = true;
                dialog.Title = "名前を付けて中間言語を保存";
                if (this._settingsManager.Settings.SoundOutput.SaveText)
                {
                    dialog.OverwritePrompt = false;
                    dialog.FileOk += new CancelEventHandler(this.sfd_FileOk);
                }
                if (dialog.ShowDialog(this._view) == DialogResult.OK)
                {
                    this.SaveKana(dialog.FileName);
                    if (this._settingsManager.Settings.SoundOutput.SaveText)
                    {
                        try
                        {
                            using (StreamWriter writer = new StreamWriter(GetTextFilePathFromWaveFilePath(dialog.FileName), false, Encoding.GetEncoding("Shift_JIS")))
                            {
                                writer.Write(Common.ReplaceNewLine(this._appVariables.SynthText));
                            }
                        }
                        catch (Exception exception)
                        {
                            MessageBox.Show(this._view, "テキストの保存に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                        }
                    }
                    this._settingsManager.Settings.KanaDirectoryPath = Path.GetDirectoryName(dialog.FileName);
                }
            }
        }

        private void SaveText(string fileName)
        {
            try
            {
                using (StreamWriter writer = new StreamWriter(fileName, false, Encoding.GetEncoding("Shift_JIS")))
                {
                    writer.Write(Common.ReplaceNewLine(this._view.MainText));
                }
            }
            catch (Exception exception)
            {
                MessageBox.Show(this._view, "テキストの保存に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
            }
            this._view.MainTextModified = false;
        }

        private void SaveTextAs()
        {
            using (SaveFileDialog dialog = new SaveFileDialog())
            {
                dialog.CheckPathExists = true;
                dialog.DefaultExt = "txt";
                dialog.FileName = this._appVariables.TextFilePath;
                dialog.Filter = "テキストファイル (*.txt)|*.txt|すべてのファイル (*.*)|*.*";
                dialog.InitialDirectory = this._settingsManager.Settings.TextDirectoryPath;
                dialog.RestoreDirectory = true;
                dialog.Title = "名前を付けてテキストを保存";
                if (dialog.ShowDialog(this._view) == DialogResult.OK)
                {
                    this.SaveText(dialog.FileName);
                    this._settingsManager.Settings.TextDirectoryPath = Path.GetDirectoryName(dialog.FileName);
                    this._appVariables.TextFilePath = dialog.FileName;
                    this._view.TextFileName = Path.GetFileName(dialog.FileName);
                }
            }
        }

        private void SaveWave(SynthMode synthMode, string inputText)
        {
            if ((synthMode == SynthMode.TextToWave) || (synthMode == SynthMode.Synthesize))
            {
                this._appVariables.Progress = 0;
                this._appVariables.WaveList.Clear();
                this.PrepareSynth();
                AITalkResultCode key = this._aitalk.Do(synthMode, inputText, this.GetSynthOption(true));
                if (key != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    if (key != AITalkResultCode.AITALKERR_INVALID_ARGUMENT)
                    {
                        MessageBox.Show(this._view, "音声保存に失敗しました。" + Environment.NewLine + AITalkErrorMessage.GetErrorMessage(key), "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    }
                }
                else
                {
                    string waveFilePath = "";
                    using (SaveFileDialog dialog = new SaveFileDialog())
                    {
                        dialog.FileName = "";
                        dialog.DefaultExt = this._settingsManager.Settings.SoundOutput.FileHeader ? "wav" : "raw";
                        dialog.Filter = this._settingsManager.Settings.SoundOutput.FileHeader ? "WAVEファイル (*.wav)|*.wav|すべてのファイル (*.*)|*.*" : "RAWファイル (*.raw)|*.raw|すべてのファイル (*.*)|*.*";
                        dialog.FilterIndex = 1;
                        dialog.InitialDirectory = this._settingsManager.Settings.WaveDirectoryPath;
                        dialog.RestoreDirectory = true;
                        dialog.Title = "音声ファイルの保存";
                        if (this._settingsManager.Settings.SoundOutput.SaveText)
                        {
                            dialog.OverwritePrompt = false;
                            dialog.FileOk += new CancelEventHandler(this.sfd_FileOk);
                        }
                        if (DialogResult.OK != dialog.ShowDialog())
                        {
                            this._aitalk.Abort();
                            this._appVariables.Clear();
                            return;
                        }
                        waveFilePath = dialog.FileName;
                        this._settingsManager.Settings.WaveDirectoryPath = Path.GetDirectoryName(dialog.FileName);
                    }
                    if (this._appVariables.Progress < 0x65)
                    {
                        SaveWaveArgs argument = new SaveWaveArgs(synthMode, waveFilePath, inputText);
                        using (ProgressView view = new ProgressView("音声保存", new DoWorkEventHandler(this.SaveWave_DoWork), argument, synthMode == SynthMode.TextToWave, true))
                        {
                            switch (view.ShowDialog())
                            {
                                case DialogResult.Abort:
                                    this._aitalk.Abort();
                                    MessageBox.Show(view.Error.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                                    this._appVariables.Clear();
                                    return;

                                case DialogResult.Cancel:
                                    this._aitalk.Abort();
                                    MessageBox.Show("音声保存を中止しました。", "注意", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                                    this._appVariables.Clear();
                                    return;
                            }
                        }
                    }
                    this._appVariables.Clear();
                }
            }
        }

        private void SaveWave_DoWork(object sender, DoWorkEventArgs e)
        {
            AIAudio_TWaveFormat format;
            BackgroundWorker bw = (BackgroundWorker) sender;
            this.ShowProgress(bw, e, "音声合成を行なっています。");
            bw.ReportProgress(100, "音声データをファイルに書き込んでいます。");
            format.formatTag = this._settingsManager.Settings.SoundOutput.DataFormat;
            format.header = this._settingsManager.Settings.SoundOutput.FileHeader ? 1 : 0;
            format.hzSamplesPerSec = this._settingsManager.Settings.SoundOutput.SamplePerSec;
            short[] wave = CatWave(this._appVariables.WaveList);
            SaveWaveArgs argument = (SaveWaveArgs) ((DoWorkEventArgsEx) e.Argument).Argument;
            if (this._aitalk.SaveWave(argument.WaveFilePath, ref format, wave) != AIAudioResultCode.AIAUDIOERR_SUCCESS)
            {
                throw new Exception("音声ファイルの保存に失敗しました。");
            }
            if (this._settingsManager.Settings.SoundOutput.SaveText && (argument.SynthMode == SynthMode.TextToWave))
            {
                try
                {
                    using (StreamWriter writer = new StreamWriter(argument.TextFilePath, false, Encoding.GetEncoding("Shift_JIS")))
                    {
                        writer.Write(Common.ReplaceNewLine(argument.SynthText));
                    }
                }
                catch (Exception exception)
                {
                    throw new Exception("テキストファイルの保存に失敗しました。" + exception.Message);
                }
            }
            this._appVariables.Progress = 0x65;
        }

        private AITalkResultCode SetSettings(UserSettings settings)
        {
            AITalk_TTtsParam param = new AITalk_TTtsParam();
            AITalkResultCode code = this._aitalk.GetParam(ref param);
            if (code == AITalkResultCode.AITALKERR_SUCCESS)
            {
                param.lenRawBufBytes = 0x158880;
                param.voiceName = settings.SelectedVoiceName;
                param.volume = settings.MasterVolume;
                this._aitalk.BeginPause = settings.BeginPause;
                this._aitalk.TermPause = settings.TermPause;
                UserSettings.VoiceSettings commonVoice = settings.CommonVoice;
                for (int i = 0; i < param.numSpeakers; i++)
                {
                    param.Speaker[i].volume = commonVoice.Volume;
                    param.Speaker[i].speed = commonVoice.Speed;
                    param.Speaker[i].pitch = commonVoice.Pitch;
                    param.Speaker[i].range = commonVoice.Emphasis;
                    param.Speaker[i].pauseMiddle = commonVoice.MiddlePause;
                    param.Speaker[i].pauseLong = commonVoice.LongPause;
                    param.Speaker[i].pauseSentence = commonVoice.SentencePause;
                }
                code = this._aitalk.SetParam(ref param);
                if (code != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    return code;
                }
            }
            return code;
        }

        private void sfd_FileOk(object sender, CancelEventArgs e)
        {
            SaveFileDialog dialog = (SaveFileDialog) sender;
            string textFilePathFromWaveFilePath = GetTextFilePathFromWaveFilePath(dialog.FileName);
            string fileName = "";
            if (File.Exists(dialog.FileName) && File.Exists(textFilePathFromWaveFilePath))
            {
                fileName = dialog.FileName + " および " + Path.GetFileName(textFilePathFromWaveFilePath);
            }
            else if (File.Exists(dialog.FileName))
            {
                fileName = dialog.FileName;
            }
            else if (File.Exists(dialog.FileName))
            {
                fileName = textFilePathFromWaveFilePath;
            }
            else
            {
                return;
            }
            if (MessageBox.Show("ファイル " + fileName + " は既に存在します。" + Environment.NewLine + "置き換えますか？", dialog.Title, MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2) != DialogResult.Yes)
            {
                e.Cancel = true;
            }
        }

        [DllImport("shell32.dll", EntryPoint="ShellExecuteA")]
        public static extern IntPtr ShellExecute(IntPtr hwnd, string lpVerb, string lpFile, string lpParameters, string lpDirectory, int nShowCmd);
        private void ShowProgress(BackgroundWorker bw, DoWorkEventArgs e, string message)
        {
            ProgressView parent = (ProgressView) ((DoWorkEventArgsEx) e.Argument).Parent;
            if (!parent.UseProgressBar)
            {
                int num = 0;
                int percentProgress = 0;
                do
                {
                    bw.ReportProgress(percentProgress, message);
                    Thread.Sleep(100);
                    num += 100;
                    if (num == 0x7d0)
                    {
                        num = 0;
                        percentProgress++;
                        if (percentProgress == 3)
                        {
                            percentProgress = 0;
                        }
                    }
                }
                while (this._appVariables.Progress < 100);
            }
            else
            {
                do
                {
                    bw.ReportProgress(this._appVariables.Progress, message);
                    Thread.Sleep(100);
                }
                while (this._appVariables.Progress < 100);
            }
        }

        private void StopSpeech(bool hightlightTeardown = false)
        {
            if (this._view.ViewStatus != ViewStatusCode.Edit)
            {
                this._aitalk.StopAudio();
                this._view.ResetLipSync();
                if (hightlightTeardown)
                {
                    this._view.HighlightTeardown(false);
                }
                this._view.ViewStatus = ViewStatusCode.Edit;
            }
        }

        public void tsmiExit_Click(object sender, EventArgs e)
        {
            this._view.Close();
        }

        public void tsmiExportSettings_Click(object sender, EventArgs e)
        {
            using (SaveFileDialog dialog = new SaveFileDialog())
            {
                string userSettingsFileExtension = Common.UserSettingsFileExtension;
                dialog.CheckPathExists = true;
                dialog.DefaultExt = userSettingsFileExtension;
                dialog.FileName = "";
                dialog.Filter = "設定ファイル (*." + userSettingsFileExtension + ")|*." + userSettingsFileExtension + "|すべてのファイル (*.*)|*.*";
                dialog.InitialDirectory = this._settingsManager.Settings.CommonDirectoryPath;
                dialog.RestoreDirectory = true;
                dialog.Title = "名前を付けて設定を保存";
                if (dialog.ShowDialog(this._view) == DialogResult.OK)
                {
                    this.UpdateSoundEffectSetting();
                    try
                    {
                        this._settingsManager.Write(dialog.FileName);
                    }
                    catch (Exception exception)
                    {
                        MessageBox.Show(this._view, "設定のエクスポートに失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    }
                    this._settingsManager.Settings.CommonDirectoryPath = Path.GetDirectoryName(dialog.FileName);
                }
            }
        }

        public void tsmiImportSettings_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog dialog = new OpenFileDialog())
            {
                string userSettingsFileExtension = Common.UserSettingsFileExtension;
                dialog.CheckPathExists = true;
                dialog.DefaultExt = userSettingsFileExtension;
                dialog.FileName = "";
                dialog.Filter = "設定ファイル (*." + userSettingsFileExtension + ")|*." + userSettingsFileExtension + "|すべてのファイル (*.*)|*.*";
                dialog.InitialDirectory = this._settingsManager.Settings.CommonDirectoryPath;
                dialog.RestoreDirectory = true;
                dialog.Title = "設定をインポート";
                if (dialog.ShowDialog(this._view) == DialogResult.OK)
                {
                    try
                    {
                        this._settingsManager.Read(dialog.FileName, this._appSettings);
                        this.ImportSettings();
                    }
                    catch (Exception exception)
                    {
                        MessageBox.Show(this._view, "設定のインポートに失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    }
                    this._settingsManager.Settings.CommonDirectoryPath = Path.GetDirectoryName(dialog.FileName);
                }
            }
        }

        public void tsmiKanaSetting_Click(object sender, EventArgs e)
        {
            using (KanaSettingView view = new KanaSettingView(this, this._settingsManager.Settings))
            {
                view.ShowDialog();
            }
        }

        public void tsmiKanaSpec_Click(object sender, EventArgs e)
        {
            if (((int) ShellExecute(GetDesktopWindow(), "Open", Path.Combine(Application.StartupPath, Common.KanaSpecFileName), "", "", 1)) <= 0x20)
            {
                MessageBox.Show(this._view, "ドキュメントを開けません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
            }
        }

        public void tsmiLangDicSetting_Click(object sender, EventArgs e)
        {
            this.UpdateSoundEffectSetting();
            using (LangDicSettingView view = new LangDicSettingView(this, this._appSettings, this._settingsManager.Settings))
            {
                view.ShowDialog();
            }
        }

        public void tsmiNewText_Click(object sender, EventArgs e)
        {
            if (!this._view.MainTextModified || (DialogResult.Yes == MessageBox.Show(this._view, "テキストが変更されています。" + Environment.NewLine + "破棄してよろしいですか？", "注意", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2)))
            {
                this._appVariables.TextFilePath = "";
                this._view.TextFileName = "";
                this._view.MainText = "";
                this._view.MainTextModified = false;
            }
        }

        public void tsmiOpenKana_Click(object sender, EventArgs e)
        {
            if (!this._view.KanaEditModified || (DialogResult.Yes == MessageBox.Show(this._view, "中間言語が変更されています。" + Environment.NewLine + "破棄してよろしいですか？", "注意", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2)))
            {
                using (OpenFileDialog dialog = new OpenFileDialog())
                {
                    string kanaFileExtension = Common.KanaFileExtension;
                    dialog.CheckPathExists = true;
                    dialog.DefaultExt = kanaFileExtension;
                    dialog.FileName = "";
                    dialog.Filter = "中間言語ファイル (*." + kanaFileExtension + ")|*." + kanaFileExtension + "|すべてのファイル (*.*)|*.*";
                    dialog.InitialDirectory = this._settingsManager.Settings.KanaDirectoryPath;
                    dialog.RestoreDirectory = true;
                    dialog.Title = "中間言語を開く";
                    if (dialog.ShowDialog(this._view) == DialogResult.OK)
                    {
                        this.OpenKana(dialog.FileName);
                    }
                }
            }
        }

        public void tsmiOpenText_Click(object sender, EventArgs e)
        {
            if (!this._view.MainTextModified || (DialogResult.Yes == MessageBox.Show(this._view, "テキストが変更されています。" + Environment.NewLine + "破棄してよろしいですか？", "注意", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2)))
            {
                using (OpenFileDialog dialog = new OpenFileDialog())
                {
                    dialog.CheckPathExists = true;
                    dialog.DefaultExt = "txt";
                    dialog.FileName = this._appVariables.TextFilePath;
                    dialog.Filter = "テキストファイル (*.txt)|*.txt|すべてのファイル (*.*)|*.*";
                    dialog.InitialDirectory = this._settingsManager.Settings.TextDirectoryPath;
                    dialog.RestoreDirectory = true;
                    dialog.Title = "テキストを開く";
                    if (dialog.ShowDialog(this._view) == DialogResult.OK)
                    {
                        this.OpenText(dialog.FileName);
                    }
                }
            }
        }

        public void tsmiOperatingManual_Click(object sender, EventArgs e)
        {
            if (((int) ShellExecute(GetDesktopWindow(), "Open", Path.Combine(Application.StartupPath, Common.OperatingManualFileName), "", "", 1)) <= 0x20)
            {
                MessageBox.Show(this._view, "操作マニュアルを開けません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
            }
        }

        public void tsmiRubySpec_Click(object sender, EventArgs e)
        {
            if (((int) ShellExecute(GetDesktopWindow(), "Open", Path.Combine(Application.StartupPath, Common.RubySpecFileName), "", "", 1)) <= 0x20)
            {
                MessageBox.Show(this._view, "ドキュメントを開けません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
            }
        }

        public void tsmiSaveText_Click(object sender, EventArgs e)
        {
            if (this._appVariables.TextFilePath != "")
            {
                this.SaveText(this._appVariables.TextFilePath);
            }
            else
            {
                this.SaveTextAs();
            }
        }

        public void tsmiSaveTextAs_Click(object sender, EventArgs e)
        {
            this.SaveTextAs();
        }

        public void tsmiSoundOutputSetting_Click(object sender, EventArgs e)
        {
            this.UpdateSoundEffectSetting();
            using (SoundOutputSettingView view = new SoundOutputSettingView(this, this._appSettings, this._settingsManager.Settings))
            {
                view.ShowDialog();
            }
        }

        public void tsmiVersionInfo_Click(object sender, EventArgs e)
        {
            string str;
            if (AITalkEditorAPI.GetLicenseDate(out str) != AITalkResultCode.AITALKERR_SUCCESS)
            {
                str = "表示できません。";
            }
            else if (str == "")
            {
                str = "無期限";
            }
            else
            {
                str = str.Substring(0, 10);
            }
            using (VersionInfoView view = new VersionInfoView(this._appSettings, str, this))
            {
                view.ShowDialog(this._view);
            }
        }

        public void tsmiVoiceDicSetting_Click(object sender, EventArgs e)
        {
            this.UpdateSoundEffectSetting();
            using (VoiceDicSettingView view = new VoiceDicSettingView(this, this._settingsManager.Settings))
            {
                view.ShowDialog();
            }
        }

        public void txtKana_DragDrop(object sender, DragEventArgs e)
        {
            if (!this._view.KanaEditModified || (DialogResult.Yes == MessageBox.Show(this._view, "中間言語が変更されています。" + Environment.NewLine + "破棄してよろしいですか？", "注意", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2)))
            {
                string[] data = (string[]) e.Data.GetData(DataFormats.FileDrop, false);
                if (data.Length != 1)
                {
                    MessageBox.Show(this._view, "中間言語の読み込みに失敗しました。" + Environment.NewLine + "複数のファイルを一度に開くことはできません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                }
                else
                {
                    this.OpenKana(data[0]);
                }
            }
        }

        public void txtMain_DragDrop(object sender, DragEventArgs e)
        {
            if (!this._view.MainTextModified || (DialogResult.Yes == MessageBox.Show(this._view, "テキストが変更されています。" + Environment.NewLine + "破棄してよろしいですか？", "注意", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button2)))
            {
                string[] data = (string[]) e.Data.GetData(DataFormats.FileDrop, false);
                if (data.Length != 1)
                {
                    MessageBox.Show(this._view, "テキストの読み込みに失敗しました。" + Environment.NewLine + "複数のファイルを一度に開くことはできません。", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                }
                else
                {
                    this.OpenText(data[0]);
                }
            }
        }

        public void txtMain_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                e.Effect = DragDropEffects.Copy;
            }
            else
            {
                e.Effect = DragDropEffects.None;
            }
        }

        public void UpdateFindSetting(UserSettings.FindSettings args)
        {
            if (this._settingsManager.Settings.Find.Target != args.Target)
            {
                this._settingsManager.Settings.Find.Target = args.Target;
            }
            if (this._settingsManager.Settings.Find.Logic != args.Logic)
            {
                this._settingsManager.Settings.Find.Logic = args.Logic;
            }
            if (this._settingsManager.Settings.Find.Match != args.Match)
            {
                this._settingsManager.Settings.Find.Match = args.Match;
            }
            if (this._settingsManager.Settings.Find.PageSize != args.PageSize)
            {
                this._settingsManager.Settings.Find.PageSize = args.PageSize;
            }
            this.WriteUserSettings(this._view);
            this._userDicView.UpdateUserSettings(this._settingsManager.Settings);
        }

        public void UpdateFontSetting(Color foreColor, Font font)
        {
            this._settingsManager.Settings.TextFormat.ForeColor = foreColor;
            this._settingsManager.Settings.TextFormat.FontFamilyName = font.FontFamily.Name;
            this._settingsManager.Settings.TextFormat.Size = font.Size;
            this._settingsManager.Settings.TextFormat.Style = font.Style;
            this._settingsManager.Settings.TextFormat.Unit = font.Unit;
            this._settingsManager.Settings.TextFormat.GdiCharSet = font.GdiCharSet;
            this._settingsManager.Settings.TextFormat.GdiVerticalFont = font.GdiVerticalFont;
            this.WriteUserSettings(this._view);
        }

        public void UpdateKanaSetting()
        {
        }

        public void UpdateLangDicSetting(LangDicSettingArgs args)
        {
            using (ProgressView view = new ProgressView("日本語辞書設定", new DoWorkEventHandler(this.UpdateLangDicSetting_DoWork), args, true, false))
            {
                DialogResult result = view.ShowDialog();
                if (result == DialogResult.Abort)
                {
                    MessageBox.Show(view.Error.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                }
            }
            this._view.RefreshView(this._symbolDic);
        }

        private void UpdateLangDicSetting_DoWork(object sender, DoWorkEventArgs e)
        {
            BackgroundWorker bw = (BackgroundWorker) sender;
            Form parent = ((DoWorkEventArgsEx) e.Argument).Parent;
            LangDicSettingArgs argument = (LangDicSettingArgs) ((DoWorkEventArgsEx) e.Argument).Argument;
            bw.ReportProgress(0, "変更内容を保存しています。");
            if (this._settingsManager.Settings.LangPath != argument.LangPath)
            {
                this._settingsManager.Settings.LangPath = argument.LangPath;
                this._appVariables.Status &= ~AppStatus.LandLoaded;
            }
            this._settingsManager.Settings.UserDic.PhraseDicEnabled = argument.PhraseDicEnabled;
            this._settingsManager.Settings.UserDic.WordDicEnabled = argument.WordDicEnabled;
            this._settingsManager.Settings.UserDic.SymbolDicEnabled = argument.SymbolDicEnabled;
            if (this._settingsManager.Settings.UserDic.PhraseDicPath != argument.PhraseDicPath)
            {
                this._settingsManager.Settings.UserDic.PhraseDicPath = argument.PhraseDicPath;
            }
            if (this._settingsManager.Settings.UserDic.WordDicPath != argument.WordDicPath)
            {
                this._settingsManager.Settings.UserDic.WordDicPath = argument.WordDicPath;
            }
            if (this._settingsManager.Settings.UserDic.SymbolDicPath != argument.SymbolDicPath)
            {
                this._settingsManager.Settings.UserDic.SymbolDicPath = argument.SymbolDicPath;
            }
            this.WriteUserSettings(parent);
            bool reset = (this._appVariables.Status & AppStatus.LandLoaded) != AppStatus.LandLoaded;
            this.InitializeLangDic(reset, parent, bw, 10, 100);
            bw.ReportProgress(100, "日本語辞書設定を更新しました。");
            Thread.Sleep(200);
        }

        public void UpdateSettingsPaneVisible(bool settingsPaneVisible)
        {
            this._settingsManager.Settings.View.SettingsPaneVisible = settingsPaneVisible;
            this.WriteUserSettings(this._view);
        }

        private void UpdateSoundEffectSetting()
        {
            this._settingsManager.Settings.SelectedVoiceName = this._view.SelectedVoiceName;
            this._settingsManager.Settings.CommonVoice.Volume = this._view.Volume;
            this._settingsManager.Settings.CommonVoice.Speed = this._view.Speed;
            this._settingsManager.Settings.CommonVoice.Pitch = this._view.Pitch;
            this._settingsManager.Settings.CommonVoice.Emphasis = this._view.Emphasis;
            this._settingsManager.Settings.CommonVoice.MiddlePause = this._view.MiddlePause;
            this._settingsManager.Settings.CommonVoice.LongPause = this._view.LongPause;
            this._settingsManager.Settings.CommonVoice.SentencePause = this._view.SentencePause;
            this._settingsManager.Settings.MasterVolume = 1f;
            this._settingsManager.Settings.BeginPause = this._view.BeginPause;
            this._settingsManager.Settings.TermPause = this._view.TermPause;
            this._settingsManager.Settings.HandleNewLineAsSentenceEnd = this._view.HandleNewLineAsSentenceEnd;
            this.WriteUserSettings(this._view);
            this.UpdateSymbolDic();
        }

        public void UpdateSoundOutputSetting(UserSettings.SoundOutputSettings args)
        {
            if (this._settingsManager.Settings.SoundOutput.SamplePerSec != args.SamplePerSec)
            {
                this._settingsManager.Settings.SoundOutput.SamplePerSec = args.SamplePerSec;
                this._appVariables.Status &= ~AppStatus.AudioInitialized;
            }
            if (this._settingsManager.Settings.SoundOutput.DataFormat != args.DataFormat)
            {
                this._settingsManager.Settings.SoundOutput.DataFormat = args.DataFormat;
                this._appVariables.Status &= ~AppStatus.AudioInitialized;
            }
            this._settingsManager.Settings.SoundOutput.FileHeader = args.FileHeader;
            this._settingsManager.Settings.SoundOutput.SaveText = args.SaveText;
            this.WriteUserSettings(this._view);
            if ((this._appVariables.Status & AppStatus.AudioInitialized) != AppStatus.AudioInitialized)
            {
                this.InitializeAudio(true, null, null, 0);
            }
            this._view.RefreshView(null);
        }

        public void UpdateSymbolDic()
        {
            if ((this._appVariables.Status & AppStatus.SymbolDicEditable) == AppStatus.SymbolDicEditable)
            {
                SymbolEntry[] entryArray = this._view.RetrieveSymbols();
                try
                {
                    for (int i = 0; i < Common.SymbolList.Length; i++)
                    {
                        if (entryArray[i].PauseLength != 0)
                        {
                            this._symbolDic.Add(entryArray[i], true);
                        }
                        else
                        {
                            int index = this._symbolDic.CheckExistence(entryArray[i]);
                            if (index >= 0)
                            {
                                this._symbolDic.RemoveAt(index);
                            }
                        }
                    }
                    this._symbolDic.Write(this._settingsManager.Settings.UserDic.SymbolDicPath);
                }
                catch (Exception exception)
                {
                    MessageBox.Show(this._view, "記号ポーズ辞書の更新に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                    return;
                }
                try
                {
                    this.ReloadSymbolDic();
                }
                catch (Exception exception2)
                {
                    MessageBox.Show(this._view, exception2.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                }
            }
        }

        public void UpdateTuningPaneVisible(bool tuningPaneVisible)
        {
            this._settingsManager.Settings.View.TuningPaneVisible = tuningPaneVisible;
            this.WriteUserSettings(this._view);
        }

        public void UpdateVoiceDicSetting(VoiceDicSettingArgs args)
        {
            using (ProgressView view = new ProgressView("音声辞書設定", new DoWorkEventHandler(this.UpdateVoiceDicSetting_DoWork), args, true, false))
            {
                DialogResult result = view.ShowDialog();
                if (result == DialogResult.Abort)
                {
                    MessageBox.Show(view.Error.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
                }
            }
            this._view.RefreshView(this._symbolDic);
        }

        private void UpdateVoiceDicSetting_DoWork(object sender, DoWorkEventArgs e)
        {
            BackgroundWorker bw = (BackgroundWorker) sender;
            Form parent = ((DoWorkEventArgsEx) e.Argument).Parent;
            VoiceDicSettingArgs argument = (VoiceDicSettingArgs) ((DoWorkEventArgsEx) e.Argument).Argument;
            bw.ReportProgress(0, "変更内容を保存しています。");
            if (this._settingsManager.Settings.DbsPath != argument.DbsPath)
            {
                this._settingsManager.Settings.DbsPath = argument.DbsPath;
                this._appVariables.Status = AppStatus.None;
            }
            if (this._settingsManager.Settings.VoiceSamplePerSec != argument.VoiceSamplePerSec)
            {
                this._settingsManager.Settings.VoiceSamplePerSec = argument.VoiceSamplePerSec;
                this._settingsManager.Settings.SoundOutput.SamplePerSec = argument.VoiceSamplePerSec;
                this._settingsManager.Settings.SoundOutput.DataFormat = AIAudioFormatType.AIAUDIOTYPE_PCM_16;
                this._appVariables.Status = AppStatus.None;
            }
            this._settingsManager.Settings.IgnoredVoiceNames = argument.IgnoredVoiceNames;
            this._settingsManager.Settings.SelectedVoiceName = argument.SelectedVoiceName;
            this.WriteUserSettings(parent);
            if ((this._appVariables.Status & AppStatus.AITalkInitialized) != AppStatus.AITalkInitialized)
            {
                this.InitializeAITalk(true, bw, 10);
                this.InitializeAudio(false, parent, bw, 20);
                this.InitializeLangDic(false, parent, bw, 30, 50);
            }
            this.InitializeVoiceDic(parent, bw, 50, 100);
            bw.ReportProgress(100, "音声辞書設定を更新しました。");
            Thread.Sleep(200);
        }

        public void UpdateWordWrapSetting(bool wordWrap)
        {
            this._settingsManager.Settings.TextFormat.WordWrap = wordWrap;
            this.WriteUserSettings(this._view);
        }

        private void WriteLicenseKey(string licenseCode)
        {
            Registry.SetValue(this._appSettings.LicenseKeyRegistryKeyPath, this._appSettings.LicenseKeyRegistryValueName, licenseCode, RegistryValueKind.String);
        }

        private void WriteLogOnFile(string str)
        {
            string path = Path.Combine(Application.LocalUserAppDataPath, "aitalk.log");
            try
            {
                using (StreamWriter writer = new StreamWriter(path, true, Encoding.GetEncoding("Shift_JIS")))
                {
                    writer.WriteLine(str);
                }
            }
            catch (Exception exception)
            {
                MessageBox.Show("ログの保存に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand);
            }
        }

        private void WriteUserSettings(Form parent)
        {
            try
            {
                this._settingsManager.Write(Common.UserSettingsFilePath);
            }
            catch (Exception exception)
            {
                Common.MessageBox.Show(parent, "設定ファイルの保存に失敗しました。" + Environment.NewLine + exception.Message, "エラー", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
            }
        }

        public class InitializeException : Exception
        {
        }

        private class SaveWaveArgs
        {
            public AITalk.SynthMode SynthMode;
            public string SynthText;
            public string TextFilePath;
            public string WaveFilePath;

            public SaveWaveArgs(AITalk.SynthMode synthMode, string waveFilePath, string synthText)
            {
                this.SynthMode = synthMode;
                this.WaveFilePath = waveFilePath;
                this.TextFilePath = MainPresenter.GetTextFilePathFromWaveFilePath(waveFilePath);
                this.SynthText = synthText;
            }
        }
    }
}

