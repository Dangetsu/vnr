
/****************************************************************************
** Copyright (c) 2006 - 2011, the LibQxt project.
** See the Qxt AUTHORS file for a list of authors and copyright holders.
** All rights reserved.
**
** Redistribution and use in source and binary forms, with or without
** modification, are permitted provided that the following conditions are met:
**     * Redistributions of source code must retain the above copyright
**       notice, this list of conditions and the following disclaimer.
**     * Redistributions in binary form must reproduce the above copyright
**       notice, this list of conditions and the following disclaimer in the
**       documentation and/or other materials provided with the distribution.
**     * Neither the name of the LibQxt project nor the
**       names of its contributors may be used to endorse or promote products
**       derived from this software without specific prior written permission.
**
** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
** ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
** WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
** DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
** DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
** (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
** LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
** ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
** (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
** SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
**
** <http://libqxt.org>  <foundation@libqxt.org>
*****************************************************************************/


/*!
    \class QxtJSON
    \inmodule QxtCore
    \brief The QxtJSON class implements serializing/deserializing from/to JSON

    implements JSON (JavaScript Object Notation) is a lightweight data-interchange format. 
    see http://www.json.org/

    \section2 Type Conversion
    \table 80%
    \header \o JSON Type \o Qt Type
    \row  \o object \o QVariantMap/QVariantHash
    \row  \o array \o QVariantList/QStringList
    \row  \o string \o QString
    \row  \o number \o int,double
    \row  \o true \o bool
    \row  \o false \o bool
    \row  \o null \o QVariant()

    \endtable

*/

#include "qxtjson.h"
#include <QVariant>
#include <QDebug>
#include <QTextStream>
#include <QStringList>

QString QxtJSON::stringify(QVariant v){
    if (v.isNull()){
        return "null";
    }
    switch (v.type()) {
        case QVariant::Bool:
            return v.toBool()?"true":"false";
            break;
        case QVariant::ULongLong:
        case QVariant::UInt:
            return QString::number(v.toULongLong());
            break;
        case QVariant::LongLong:
        case QVariant::Int:
            return QString::number(v.toLongLong());
            break;
        case QVariant::Double:
            return QString::number(v.toDouble());
            break;
        case QVariant::Map:
            {
                QString r="{";
                QMap<QString, QVariant> map = v.toMap();
                QMapIterator<QString, QVariant> i(map);
                while (i.hasNext()){
                    i.next();
                    r+="\""+i.key()+"\":"+stringify(i.value())+",";
                }
                if(r.length()>1)
                    r.chop(1);
                r+="}";
                return r;
            }
            break;
#if QT_VERSION >= 0x040500
        case QVariant::Hash:
            {
                QString r="{";
                QHash<QString, QVariant> map = v.toHash();
                QHashIterator<QString, QVariant> i(map);
                while (i.hasNext()){
                    i.next();
                    r+="\""+i.key()+"\":"+stringify(i.value())+",";
                }
                if(r.length()>1)
                    r.chop(1);
                r+="}";
                return r;
            }
            break;
#endif
        case QVariant::StringList:
            {
                QString r="[";
                QStringList l = v.toStringList();
                foreach(QString i, l){
                    r+="\""+i+"\",";
                }
                if(r.length()>1)
                    r.chop(1);
                r+="]";
                return r;
            }
        case QVariant::List:
            {
                QString r="[";
                QVariantList l = v.toList();
                foreach(QVariant i, l){
                    r+=stringify(i)+",";
                }
                if(r.length()>1)
                    r.chop(1);
                r+="]";
                return r;
            }
            break;
        case QVariant::String:
        default:
            {
                QString in = v.toString();
                QString out;
                for(QString::ConstIterator i = in.constBegin(); i != in.constEnd(); i++){
                    if( (*i) == QChar('\b'))
                        out.append("\\b");
                    else if( (*i) == QChar('\f'))
                        out.append("\\f");
                    else if( (*i) == QChar('\n'))
                        out.append("\\n");
                    else if( (*i) == QChar('\r'))
                        out.append("\\r");
                    else if( (*i) == QChar('\t'))
                        out.append("\\t");
                    else if( (*i) == QChar('\f'))
                        out.append("\\f");
                    else if( (*i) == QChar('\\'))
                        out.append("\\\\");
                    else if( (*i) == QChar('/'))
                        out.append("\\/");
                    else
                        out.append(*i);
                }
                return "\""+out+"\"";
            }
            break;
    }
    return QString();
}

static QVariant parseValue(QTextStream &s,bool & error);
static QVariantMap parseObject (QTextStream & s,bool & error);
static QVariantList parseArray (QTextStream & s,bool & error);
static QString parseString (QTextStream & s,bool & error);
static QVariant parseLiteral (QTextStream & s,bool & error);

QVariant QxtJSON::parse(QString string){
    QTextStream s(&string);
    bool error=false;
    QVariant v=parseValue(s,error);
    if(error)
        return QVariant();
    return v;
}



static QVariant parseValue(QTextStream &s,bool & error){
    s.skipWhiteSpace();
    QChar c;
    while(!s.atEnd() && !error){
        s>>c;
        if (c=='{'){
            return parseObject(s,error);
        } else if (c=='"'){
            return parseString(s,error);
        } else if (c=='['){
            return parseArray(s,error);
        } else {
            return parseLiteral(s,error);
        }
        s.skipWhiteSpace();
    }
    return QVariant();
}

static QVariantMap parseObject (QTextStream & s,bool & error){
    s.skipWhiteSpace();
    QVariantMap o;
    QString key;
    bool atVal=false;

    QChar c;
    while(!s.atEnd() && !error){
        s>>c;
        if (c=='}'){
            return o;
        } else if (c==',' || c==':'){
            /*
              They're syntactic sugar, since key:value come in bundles anyway
              Could check for error handling. too lazy.
            */
        } else if (c=='"'){
            if(atVal){
                o[key]=parseString(s,error);
                atVal=false;
            }else{
                key=parseString(s,error);
                atVal=true;
            }
        } else if (c=='['){
            if(atVal){
                o[key]=parseArray(s,error);
                atVal=false;
            }else{
                error=true;
                return QVariantMap();
            }
        } else if (c=='{'){
            if(atVal){
                o[key]=parseObject(s,error);
                atVal=false;
            }else{
                error=true;
                return QVariantMap();
            }
        } else {
            if(atVal){
                o[key]=parseLiteral(s,error);
                atVal=false;
            }else{
                error=true;
                return QVariantMap();
            }
        }
        s.skipWhiteSpace();
    }
    error=true;
    return QVariantMap();
}
static QVariantList parseArray (QTextStream & s,bool & error){
    s.skipWhiteSpace();
    QVariantList l;
    QChar c;
    while(!s.atEnd() && !error){
        s>>c;
        if (c==']'){
            return l;
        } else if (c==','){
        } else if (c=='"'){
            l.append(QVariant(parseString(s,error)));
        } else if (c=='['){
            l.append(QVariant(parseArray(s,error)));
        } else if (c=='{'){
            l.append(QVariant(parseObject(s,error)));
        } else {
            l.append(QVariant(parseLiteral(s,error)));
        }
        s.skipWhiteSpace();
    }
    error=true;
    return QVariantList();
}
static QString parseString (QTextStream & s,bool & error){
    QString str;
    QChar c;
    while(!s.atEnd() && !error){
        s>>c;
        if(c=='"'){
            return str;
        }else if(c=='\\'){
            s>>c;
            if(c=='b'){
                str.append('\b');
            }else if(c=='f'){
                str.append('\f');
            }else if(c=='n'){
                str.append('\n');
            }else if(c=='r'){
                str.append('\r');
            }else if(c=='t'){
                str.append('\t');
            }else if(c=='f'){
                str.append('\f');
            }else if(c=='u'){
                QString k;
                for (int i = 0; i < 4; i++ ) {
                    s >> c;
                    k.append(c);
                }
                bool ok;
                int i = k.toInt(&ok, 16);
                if (ok)
                    str.append(QChar(i));
            }else{
                str.append(c);
            }
        }else{
            str.append(c);
        }
    }
    error=true;
    return QString();
}
static QVariant parseLiteral (QTextStream & s,bool & error){
    s.seek(s.pos()-1);
    QChar c;
    while(!s.atEnd() && !error){
        s>>c;
        if (c=='t'){
            s>>c;//r
            s>>c;//u
            s>>c;//e
            return true;
        } else if (c=='f'){
            s>>c;//a
            s>>c;//l
            s>>c;//s
            s>>c;//e
            return false;
        }else if (c=='n'){
            s>>c;//u
            s>>c;//l
            s>>c;//l
            return QVariant();
        }else if (c=='-' || c.isDigit()){
            QString n;
            while(( c.isDigit()  || (c=='.') || (c=='E') || (c=='e') || (c=='-') || (c=='+') )){
                n.append(c);
                if(s.atEnd() ||  error)
                    break;
                s>>c;
            }
            s.seek(s.pos()-1);
            if(n.contains('.')) {
                return n.toDouble();
            } else {
                bool ok = false;
                int result = n.toInt(&ok);
                if(ok) return result;
                return n.toLongLong();
            }
        }
    }
    error=true;
    return QVariant();
}
