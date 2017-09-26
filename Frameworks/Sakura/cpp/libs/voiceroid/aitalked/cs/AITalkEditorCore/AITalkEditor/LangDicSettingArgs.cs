namespace AITalkEditor
{
    using System;

    public class LangDicSettingArgs
    {
        public string LangPath;
        public bool PhraseDicEnabled;
        public string PhraseDicPath;
        public bool SymbolDicEnabled;
        public string SymbolDicPath;
        public bool WordDicEnabled;
        public string WordDicPath;

        public LangDicSettingArgs(string langPath, bool wordDicEnabled, bool phraseDicEnabled, bool symbolDicEnabled, string wordDicPath, string phraseDicPath, string symbolDicPath)
        {
            this.LangPath = langPath;
            this.WordDicEnabled = wordDicEnabled;
            this.PhraseDicEnabled = phraseDicEnabled;
            this.SymbolDicEnabled = symbolDicEnabled;
            this.WordDicPath = wordDicPath;
            this.PhraseDicPath = phraseDicPath;
            this.SymbolDicPath = symbolDicPath;
        }
    }
}

