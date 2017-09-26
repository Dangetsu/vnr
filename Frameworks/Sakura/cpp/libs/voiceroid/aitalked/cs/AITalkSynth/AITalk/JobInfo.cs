namespace AITalk
{
    using System;
    using System.Collections.Generic;
    using System.Runtime.CompilerServices;
    using System.Runtime.InteropServices;
    using System.Text;

    public class JobInfo
    {
        private static Encoding _sjisEnc = Encoding.GetEncoding("Shift_JIS");
        internal Queue<AITalkUtilEx.AudioEventParam> AudioEventQueue;
        public int BeginPause;
        internal StringBuilder KanaBuffer;
        public int TermPause;
        public List<TextBlock> TextBlockList;
        internal short[] WaveBuffer;

        public JobInfo(SynthMode synthMode, string text, SynthOption synthOption, uint kanaBufBytes, uint waveBufBytes)
        {
            this.JobID = 0;
            this.BeginPause = 0;
            this.TermPause = 0;
            this.KanaBuffer = new StringBuilder((int) kanaBufBytes);
            this.WaveBuffer = new short[waveBufBytes / 2];
            this.Text = text;
            if ((synthOption & SynthOption.IgnoreNewLine) == SynthOption.IgnoreNewLine)
            {
                this.IgnoreNewLine = true;
                this.SynthText = this.Text.Replace("\n", null);
                this.MakePosConvertTable();
            }
            else
            {
                this.IgnoreNewLine = false;
                this.SynthText = this.Text;
                this.MakePosConvertTable();
            }
            this.CurrentTextPos = 0;
            this.LastBookmarkPos = 0;
            this.TextProcessingDone = (synthMode & SynthMode.TextProcess) != SynthMode.TextProcess;
            this.SynthesizingDone = (synthMode & SynthMode.Synthesize) != SynthMode.Synthesize;
            this.Aborted = false;
            this.TextProcessingProgress = 0;
            this.SynthesizingProgress = 0;
            this.CurrentIndex = 0;
            this.NextSentenceStartTick = 0L;
            this.TextBlockList = new List<TextBlock>();
            this.AudioEventQueue = new Queue<AITalkUtilEx.AudioEventParam>();
        }

        public TextBlock AddTextBlock(int endPos, string kana)
        {
            TextBlock block;
            int num = this.PosConvertTable[endPos];
            int num2 = num - 1;
            while ((num2 >= this.CurrentTextPos) && (this.Text[num2] == '\n'))
            {
                num2--;
            }
            num2--;
            while (num2 >= this.CurrentTextPos)
            {
                if (CheckTerminalSymbol(this.Text[num2], this.IgnoreNewLine))
                {
                    this.CurrentTextPos = num2 + 1;
                    break;
                }
                num2--;
            }
            string text = this.Text.Substring(this.CurrentTextPos, num - this.CurrentTextPos);
            if (this.TextBlockList.Count > 0)
            {
                TextBlock block2 = this.TextBlockList[this.TextBlockList.Count - 1];
                block = new TextBlock(this.CurrentTextPos, text, kana, block2.VoiceName, block2.Volume, block2.Speed, block2.Pitch, block2.Emphasis);
            }
            else
            {
                block = new TextBlock(this.CurrentTextPos, text, kana, "", 1f, 1f, 1f, 1f);
            }
            this.TextBlockList.Add(block);
            this.CurrentTextPos = num;
            return block;
        }

        private static bool CheckTerminalSymbol(char c, bool ignoreNewLine)
        {
            foreach (char ch in AITalkUtilEx.TerminalSymbolList)
            {
                if ((!ignoreNewLine || (ch != '\n')) && (ch == c))
                {
                    return true;
                }
            }
            return false;
        }

        public int GetSynthesizeingProgressPercentage()
        {
            if (this.Text.Length == 0)
            {
                return 0;
            }
            return (int) Math.Round((double) (((100.0 * this.SynthesizingProgress) / ((double) this.Text.Length)) + 1.0));
        }

        public int GetTextProcessingProgressPercentage()
        {
            if (this.Text.Length == 0)
            {
                return 0;
            }
            return (int) Math.Round((double) (((100.0 * this.TextProcessingProgress) / ((double) this.Text.Length)) + 1.0));
        }

        public void GrowSynthesizingProgress(TextBlock textBlock)
        {
            this.SynthesizingProgress = textBlock.Pos + textBlock.Text.Length;
        }

        public void GrowTextProcessingProgress(TextBlock textBlock)
        {
            this.TextProcessingProgress = textBlock.Pos + textBlock.Text.Length;
        }

        private static bool IsHalfsize(char c)
        {
            return (_sjisEnc.GetByteCount(c.ToString()) == 1);
        }

        private void MakePosConvertTable()
        {
            this.PosConvertTable = new int[(this.Text.Length * 2) + 1];
            int num = 0;
            int num2 = 0;
            num2 = 0;
            while (num2 < this.Text.Length)
            {
                if (!this.IgnoreNewLine || (this.Text[num2] != '\n'))
                {
                    this.PosConvertTable[num++] = num2;
                    if (!IsHalfsize(this.Text[num2]))
                    {
                        this.PosConvertTable[num++] = num2;
                    }
                }
                num2++;
            }
            for (int i = num; i < this.PosConvertTable.Length; i++)
            {
                this.PosConvertTable[i] = num2;
            }
        }

        internal string ProgressBookMark(string name, out int pos)
        {
            try
            {
                int num = this.PosConvertTable[uint.Parse(name)];
                int lastBookmarkPos = this.LastBookmarkPos;
                int num3 = num;
                string str = this.Text.Substring(lastBookmarkPos, num3 - lastBookmarkPos);
                this.LastBookmarkPos = num;
                pos = lastBookmarkPos;
                return str;
            }
            catch
            {
                pos = -1;
                return null;
            }
        }

        public override string ToString()
        {
            string str = "#synth units: " + this.TextBlockList.Count + Environment.NewLine;
            foreach (TextBlock block in this.TextBlockList)
            {
                str = str + block.ToString() + Environment.NewLine;
            }
            return str;
        }

        public bool Aborted { get; internal set; }

        public int CurrentIndex { get; internal set; }

        public int CurrentTextPos { get; private set; }

        public bool IgnoreNewLine { get; private set; }

        public int JobID { get; internal set; }

        public int LastBookmarkPos { get; private set; }

        public long NextSentenceStartTick { get; internal set; }

        public int[] PosConvertTable { get; private set; }

        public bool SynthesizingDone { get; internal set; }

        public int SynthesizingProgress { get; internal set; }

        public string SynthText { get; private set; }

        public string Text { get; private set; }

        public bool TextProcessingDone { get; internal set; }

        public int TextProcessingProgress { get; internal set; }

        public class TextBlock
        {
            public float Emphasis;
            public float Pitch;
            public float Speed;
            public string VoiceName;
            public float Volume;

            public TextBlock(int pos, string text, string kana, string voiceName, float volume, float speed, float pitch, float emphasis)
            {
                this.Pos = pos;
                this.Text = text;
                this.Kana = kana;
                this.Wave = null;
                this.Tick = 0L;
                this.VoiceName = voiceName;
                this.Volume = volume;
                this.Speed = speed;
                this.Pitch = pitch;
                this.Emphasis = emphasis;
            }

            public override string ToString()
            {
                return string.Concat(new object[] { this.Pos, " : ", this.Text, " : ", this.Kana, " : ", this.Tick });
            }

            public string Kana { get; internal set; }

            public int Pos { get; internal set; }

            public string Text { get; internal set; }

            public long Tick { get; internal set; }

            public short[] Wave { get; internal set; }
        }
    }
}

