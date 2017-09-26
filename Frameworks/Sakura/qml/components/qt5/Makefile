# Makefile
# 8/8/2013 jichi
include ../../qmljs.mk

QML_TARGETS = text5.qml textedit5.qml

all: Makefile $(QML_TARGETS)
clean:

text5.qml: text5.qmt
	>$@ sed -e 's/{{class}}/Text/g' $^

textedit5.qml: text5.qmt
	>$@ sed -e 's/{{class}}/TextEdit/g' $^

# EOF
