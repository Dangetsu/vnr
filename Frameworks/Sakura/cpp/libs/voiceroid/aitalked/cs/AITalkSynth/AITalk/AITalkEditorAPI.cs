namespace AITalk
{
    using System;
    using System.Runtime.InteropServices;
    using System.Text;

    public class AITalkEditorAPI
    {
        public static AITalkResultCode GetLicenseDate(out string date)
        {
            StringBuilder bufDate = new StringBuilder(30);
            AITalkResultCode code = LicenseDate(bufDate);
            date = bufDate.ToString();
            return code;
        }

        public static AITalkResultCode GetLicenseInfo(string key, out string str, int len = 0x400)
        {
            uint num;
            StringBuilder bufVal = new StringBuilder(len);
            AITalkResultCode code = LicenseInfo(key, bufVal, (uint) len, out num);
            str = bufVal.ToString();
            return code;
        }

        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_LicenseDate")]
        private static extern AITalkResultCode LicenseDate(StringBuilder bufDate);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_LicenseInfo")]
        private static extern AITalkResultCode LicenseInfo(string key, StringBuilder bufVal, uint lenVal, out uint size);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_ModuleFlag")]
        public static extern uint ModuleFlag();
    }
}

