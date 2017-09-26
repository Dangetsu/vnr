// qmleffectsplugin.cc
// 11/12/2012 jichi
#include "qmleffectsplugin/qmleffectsplugin.h"
#include "qteffects/graphicsgloweffect.h"
#include "qteffects/graphicsgloweffect2.h"
#include "qteffects/graphicstextshadoweffect.h"
#include <QtDeclarative/qdeclarative.h>

QmlEffectsPlugin::QmlEffectsPlugin(QObject *parent)
  : Base(parent) {}

void QmlEffectsPlugin::registerTypes(const char *uri)
{
  qmlRegisterType</*QtEffects::*/GraphicsTextShadowEffect>(uri, 1, 0, "TextShadow");
  qmlRegisterType</*QtEffects::*/GraphicsGlowEffect>(uri, 1, 0, "Glow");
  qmlRegisterType</*QtEffects::*/GraphicsGlowEffect2>(uri, 1, 0, "Glow2");
}

Q_EXPORT_PLUGIN2(qmleffectsplugin, QmlEffectsPlugin);

// EOF
