namespace AITalkEditor
{
    using System;
    using System.IO;
    using System.Xml.Serialization;

    public class SettingsManager
    {
        private XmlSerializer _serializer = new XmlSerializer(typeof(UserSettings));
        private UserSettings _settings;

        public void Read(string path, AppSettings appSettings)
        {
            using (FileStream stream = new FileStream(path, FileMode.Open))
            {
                try
                {
                    this._settings = (UserSettings) this._serializer.Deserialize(stream);
                }
                catch (Exception exception)
                {
                    this._settings = new UserSettings(appSettings);
                    throw exception;
                }
                if (!this._settings.Validate(appSettings))
                {
                    throw new Exception("設定ファイルのフォーマットが正しくありません。");
                }
            }
        }

        public void Write(string path)
        {
            using (FileStream stream = new FileStream(path, FileMode.Create))
            {
                this._serializer.Serialize((Stream) stream, this._settings);
            }
        }

        public UserSettings Settings
        {
            get
            {
                return this._settings;
            }
            set
            {
                this._settings = value;
            }
        }
    }
}

