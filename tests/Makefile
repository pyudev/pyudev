include bindings/bindings.mk
include bindings/pyqt.mk
include bindings/pyside.mk
include bindings/pygobject.mk

bindings = pyqt
ifeq ($(PYTHON_MAJOR),2)
bindings += pyside pygobject
endif

.PHONY: bindings
bindings : $(bindings)
