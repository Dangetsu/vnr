namespace AITalkEditor
{
    using System;
    using System.Collections.Generic;

    public class VoiceDicSettingArgs
    {
        public string DbsPath;
        public List<string> IgnoredVoiceNames;
        public string SelectedVoiceName;
        public int VoiceSamplePerSec;

        public VoiceDicSettingArgs(string dbsPath, int voiceSamplePerSec, List<string> ignoredVoiceNames, string selectecVoiceName)
        {
            this.DbsPath = dbsPath;
            this.VoiceSamplePerSec = voiceSamplePerSec;
            this.IgnoredVoiceNames = ignoredVoiceNames;
            this.SelectedVoiceName = selectecVoiceName;
        }
    }
}

