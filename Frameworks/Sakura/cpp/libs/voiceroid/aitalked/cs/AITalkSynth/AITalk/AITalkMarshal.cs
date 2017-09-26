namespace AITalk
{
    using System;
    using System.Runtime.InteropServices;
    using System.Text;

    public class AITalkMarshal
    {
        public static IntPtr AllocateTTtsParam(int voices, out int structSize)
        {
            structSize = ((((((((((4 + (Marshal.SizeOf(typeof(IntPtr)) * 3)) + 8) + 4) + 8) + 80) + 160) + 12) + 12) + 4) + 4) + (0x6c * voices);
            return Marshal.AllocCoTaskMem(structSize);
        }

        public static AITalk_TTtsParam IntPtrToTTtsParam(IntPtr pParam)
        {
            AITalk_TTtsParam param = new AITalk_TTtsParam();
            int ofs = 0;
            param.size = ReadUInt32(pParam, ref ofs);
            param.procTextBuf = (AITalkProcTextBuf) ReadDelegate(pParam, ref ofs, typeof(AITalkProcTextBuf));
            param.procRawBuf = (AITalkProcRawBuf) ReadDelegate(pParam, ref ofs, typeof(AITalkProcRawBuf));
            param.procEventTts = (AITalkProcEventTTS) ReadDelegate(pParam, ref ofs, typeof(AITalkProcEventTTS));
            param.lenTextBufBytes = ReadUInt32(pParam, ref ofs);
            param.lenRawBufBytes = ReadUInt32(pParam, ref ofs);
            param.volume = ReadSingle(pParam, ref ofs);
            param.pauseBegin = ReadInt32(pParam, ref ofs);
            param.pauseTerm = ReadInt32(pParam, ref ofs);
            param.voiceName = ReadString(pParam, ref ofs, 80);
            param.Jeita.femaleName = ReadString(pParam, ref ofs, 80);
            param.Jeita.maleName = ReadString(pParam, ref ofs, 80);
            param.Jeita.pauseMiddle = ReadInt32(pParam, ref ofs);
            param.Jeita.pauseLong = ReadInt32(pParam, ref ofs);
            param.Jeita.pauseSentence = ReadInt32(pParam, ref ofs);
            param.Jeita.control = ReadString(pParam, ref ofs, 12);
            param.numSpeakers = ReadUInt32(pParam, ref ofs);
            param.__reserved__ = ReadInt32(pParam, ref ofs);
            param.Speaker = new AITalk_TTtsParam.TSpeakerParam[param.numSpeakers];
            for (int i = 0; i < param.numSpeakers; i++)
            {
                param.Speaker[i].voiceName = ReadString(pParam, ref ofs, 80);
                param.Speaker[i].volume = ReadSingle(pParam, ref ofs);
                param.Speaker[i].speed = ReadSingle(pParam, ref ofs);
                param.Speaker[i].pitch = ReadSingle(pParam, ref ofs);
                param.Speaker[i].range = ReadSingle(pParam, ref ofs);
                param.Speaker[i].pauseMiddle = ReadInt32(pParam, ref ofs);
                param.Speaker[i].pauseLong = ReadInt32(pParam, ref ofs);
                param.Speaker[i].pauseSentence = ReadInt32(pParam, ref ofs);
            }
            return param;
        }

        public static Delegate ReadDelegate(IntPtr ptr, ref int ofs, Type type)
        {
            IntPtr ptr2 = Marshal.ReadIntPtr(ptr, ofs);
            ofs += Marshal.SizeOf(typeof(IntPtr));
            if (!(ptr2 != IntPtr.Zero))
            {
                return null;
            }
            return Marshal.GetDelegateForFunctionPointer(ptr2, type);
        }

        public static int ReadInt32(IntPtr ptr, ref int ofs)
        {
            int num = Marshal.ReadInt32(ptr, ofs);
            ofs += 4;
            return num;
        }

        public static float ReadSingle(IntPtr ptr, ref int ofs)
        {
            byte[] buffer = new byte[] { Marshal.ReadByte(ptr, ofs), Marshal.ReadByte(ptr, ofs + 1), Marshal.ReadByte(ptr, ofs + 2), Marshal.ReadByte(ptr, ofs + 3) };
            ofs += 4;
            return BitConverter.ToSingle(buffer, 0);
        }

        public static string ReadString(IntPtr ptr, ref int ofs, int len)
        {
            int index = 0;
            byte[] bytes = new byte[len];
            while (index < len)
            {
                byte num2 = Marshal.ReadByte(ptr, ofs + index);
                if (num2 == 0)
                {
                    break;
                }
                bytes[index] = num2;
                index++;
            }
            ofs += len;
            return Encoding.GetEncoding("Shift_JIS").GetString(bytes, 0, index);
        }

        public static uint ReadUInt32(IntPtr ptr, ref int ofs)
        {
            uint num = (uint) Marshal.ReadInt32(ptr, ofs);
            ofs += 4;
            return num;
        }

        public static IntPtr TTtsParamToIntPtr(ref AITalk_TTtsParam param)
        {
            int num;
            IntPtr ptr = AllocateTTtsParam((int) param.numSpeakers, out num);
            int ofs = 0;
            WriteUInt32(ptr, ref ofs, param.size);
            WriteDelegate(ptr, ref ofs, param.procTextBuf);
            WriteDelegate(ptr, ref ofs, param.procRawBuf);
            WriteDelegate(ptr, ref ofs, param.procEventTts);
            WriteUInt32(ptr, ref ofs, param.lenTextBufBytes);
            WriteUInt32(ptr, ref ofs, param.lenRawBufBytes);
            WriteSingle(ptr, ref ofs, param.volume);
            WriteInt32(ptr, ref ofs, param.pauseBegin);
            WriteInt32(ptr, ref ofs, param.pauseTerm);
            WriteString(ptr, ref ofs, param.voiceName, 80);
            WriteString(ptr, ref ofs, param.Jeita.femaleName, 80);
            WriteString(ptr, ref ofs, param.Jeita.maleName, 80);
            WriteInt32(ptr, ref ofs, param.Jeita.pauseMiddle);
            WriteInt32(ptr, ref ofs, param.Jeita.pauseLong);
            WriteInt32(ptr, ref ofs, param.Jeita.pauseSentence);
            WriteString(ptr, ref ofs, param.Jeita.control, 12);
            WriteUInt32(ptr, ref ofs, param.numSpeakers);
            WriteInt32(ptr, ref ofs, param.__reserved__);
            for (int i = 0; i < param.numSpeakers; i++)
            {
                WriteString(ptr, ref ofs, param.Speaker[i].voiceName, 80);
                WriteSingle(ptr, ref ofs, param.Speaker[i].volume);
                WriteSingle(ptr, ref ofs, param.Speaker[i].speed);
                WriteSingle(ptr, ref ofs, param.Speaker[i].pitch);
                WriteSingle(ptr, ref ofs, param.Speaker[i].range);
                WriteInt32(ptr, ref ofs, param.Speaker[i].pauseMiddle);
                WriteInt32(ptr, ref ofs, param.Speaker[i].pauseLong);
                WriteInt32(ptr, ref ofs, param.Speaker[i].pauseSentence);
            }
            return ptr;
        }

        public static void WriteDelegate(IntPtr ptr, ref int ofs, Delegate val)
        {
            IntPtr ptr2 = (val != null) ? Marshal.GetFunctionPointerForDelegate(val) : IntPtr.Zero;
            Marshal.WriteIntPtr(ptr, ofs, ptr2);
            ofs += Marshal.SizeOf(typeof(IntPtr));
        }

        public static void WriteInt32(IntPtr ptr, ref int ofs, int val)
        {
            Marshal.WriteInt32(ptr, ofs, val);
            ofs += 4;
        }

        public static void WriteSingle(IntPtr ptr, ref int ofs, float val)
        {
            byte[] bytes = BitConverter.GetBytes(val);
            for (int i = 0; i < 4; i++)
            {
                Marshal.WriteByte(ptr, ofs + i, bytes[i]);
            }
            ofs += 4;
        }

        public static void WriteString(IntPtr ptr, ref int ofs, string val, int len)
        {
            int index = 0;
            if (val != null)
            {
                byte[] bytes = Encoding.GetEncoding("Shift_JIS").GetBytes(val);
                while ((index < (len - 1)) && (index < bytes.Length))
                {
                    Marshal.WriteByte(ptr, ofs + index, bytes[index]);
                    index++;
                }
            }
            Marshal.WriteByte(ptr, ofs + index, 0);
            ofs += len;
        }

        public static void WriteUInt32(IntPtr ptr, ref int ofs, uint val)
        {
            Marshal.WriteInt32(ptr, ofs, (int) val);
            ofs += 4;
        }
    }
}

