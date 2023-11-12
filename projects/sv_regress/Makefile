
export PROJ=$(PWD)/../..
export CVRF=$(PROJ)/cvrf

DUT_FILE_LIST = $(PROJ)/src/filelist.f

ifndef VERILATOR
	include $(CVRF)/scripts/makefiles/Makefile.ms
else
	include $(CVRF)/scripts/makefiles/Makefile.vrlt
endif