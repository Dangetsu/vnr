namespace AITalkEditor.Properties
{
    using System;
    using System.CodeDom.Compiler;
    using System.ComponentModel;
    using System.Diagnostics;
    using System.Drawing;
    using System.Globalization;
    using System.Resources;
    using System.Runtime.CompilerServices;

    [DebuggerNonUserCode, CompilerGenerated, GeneratedCode("System.Resources.Tools.StronglyTypedResourceBuilder", "4.0.0.0")]
    internal class Resources
    {
        private static CultureInfo resourceCulture;
        private static System.Resources.ResourceManager resourceMan;

        internal Resources()
        {
        }

        [EditorBrowsable(EditorBrowsableState.Advanced)]
        internal static CultureInfo Culture
        {
            get
            {
                return resourceCulture;
            }
            set
            {
                resourceCulture = value;
            }
        }

        internal static Icon face
        {
            get
            {
                return (Icon) ResourceManager.GetObject("face", resourceCulture);
            }
        }

        internal static Bitmap fg00
        {
            get
            {
                return (Bitmap) ResourceManager.GetObject("fg00", resourceCulture);
            }
        }

        internal static Bitmap fg01
        {
            get
            {
                return (Bitmap) ResourceManager.GetObject("fg01", resourceCulture);
            }
        }

        internal static Bitmap logo
        {
            get
            {
                return (Bitmap) ResourceManager.GetObject("logo", resourceCulture);
            }
        }

        [EditorBrowsable(EditorBrowsableState.Advanced)]
        internal static System.Resources.ResourceManager ResourceManager
        {
            get
            {
                if (object.ReferenceEquals(resourceMan, null))
                {
                    System.Resources.ResourceManager manager = new System.Resources.ResourceManager("AITalkEditor.Properties.Resources", typeof(AITalkEditor.Properties.Resources).Assembly);
                    resourceMan = manager;
                }
                return resourceMan;
            }
        }

        internal static Bitmap version_info
        {
            get
            {
                return (Bitmap) ResourceManager.GetObject("version_info", resourceCulture);
            }
        }
    }
}

