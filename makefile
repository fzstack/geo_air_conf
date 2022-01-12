SRCS = $(wildcard *.ui)

*_ui.py: *.ui
	echo $@ $^

all: $(patsubst %.ui, %_ui.py, $(SRCS))
	echo $(patsubst %.ui, %_ui.py, $(SRCS))