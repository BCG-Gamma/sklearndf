export CONDA_BLD_PATH=dist/conda
FACET_PATH := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../)

# absolute paths to local conda "channels" with built packages:
P_PYTOOLS=$(FACET_PATH)/pytools/dist/conda

# check local path for pytools packages and if they exist,
# add them as an conda channel:
ifneq ("$(wildcard $(P_PYTOOLS))","")
    C_PYTOOLS = -c "file:/$(P_PYTOOLS)"
endif

# the final command to append to conda build so that it finds locally
# built packages:
LOCAL_CHANNELS = $(C_PYTOOLS)


help:
	@echo Usage: make package

.PHONY: help Makefile

clean:
	mkdir -p "$(CONDA_BLD_PATH)" && \
	rm -rf $(CONDA_BLD_PATH)/*

build:
	echo Creating a conda package for sklearndf && \
	FACET_PATH="$(FACET_PATH)" conda-build -c conda-forge $(LOCAL_CHANNELS) conda-build/

package: clean build
