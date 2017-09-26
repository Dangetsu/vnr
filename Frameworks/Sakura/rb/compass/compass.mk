# compass.mk
# 8/8/2013 jichi
# http://compass-style.org/help/tutorials/command-line/

ifeq ($(OS),Windows_NT)
  COMPASS = compass.bat
  YUI = yuicompressor.cmd
else
  COMPASS = compass
  YUI = yuicompressor
endif

.yui:
	$(YUI) $(OPT) --type $(TYPE) -o $(OUT) $(IN)

%.min.css: %.css
	$(MAKE) .yui TYPE=css OUT=$@ IN=$^

COMPASS_COMMANDS = compile watch clean

.PHONY: all compress $(COMPASS_COMMANDS)

# EOF
