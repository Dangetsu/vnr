# env.mk
# 8/8/2013 jichi

.PHONY: all compress download clean

WGET = wget
ifeq ($(OS),Windows_NT)
  YUI = yuicompressor.cmd
  UGLIFY = uglifyjs.cmd
  CLOSURE = closure.cmd
else
  YUI = yuicompressor
  UGLIFY = uglifyjs
  CLOSURE = closure
  #CLOSURE = closure --compilation_level ADVANCED_OPTIMIZATIONS
endif

.closure:
	$(CLOSURE) $(OPT) --js_output_file $(OUT) --js $(IN)

.uglify:
	$(UGLIFY) $(OPT) -o $(OUT) $(IN)

.wget:
	$(WGET) $(OPT) -O $(OUT) $(IN)

.yui:
ifdef TYPE
	$(YUI) $(OPT) --type $(TYPE) -o $(OUT) $(IN)
else
	$(YUI) $(OPT) -o $(OUT) $(IN)
endif

# EOF
