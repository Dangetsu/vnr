# qmljs.mk
# 8/8/2013 jichi

.PHONY: all clean compile compress download

WGET = wget
ifeq ($(OS),Windows_NT)
  CLOSURE = closure.cmd
  YUI = yuicompressor.cmd
else
  #CLOSURE = closure --compilation_level ADVANCED_OPTIMIZATIONS
  CLOSURE = closure
  YUI = yuicompressor
endif

.wget:
	$(WGET) $(OPT) -O $(OUT) $(IN)

.yui:
ifdef TYPE
	$(YUI) $(OPT) --type $(TYPE) -o $(OUT) $(IN)
else
	$(YUI) $(OPT) -o $(OUT) $(IN)
  endif

.closure:
	$(CLOSURE) $(OPT) --js_output_file $(OUT) --js $(IN)

.clean:
	rm -f *.{1,2}

.pragma:
	> $(OUT).1 sed 's/^\.pragma .*//' $(IN)
	$(MAKE) .closure IN=$(OUT).1 OUT=$(OUT).2 OPT=$(OPT)
	> $(OUT) echo '.pragma library'
	>> $(OUT) cat $(OUT).2
	dos2unix $(OUT)
	rm $(OUT).1 $(OUT).2

# EOF
