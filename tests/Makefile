include bindings/bindings.mk

QT_MODULES = QtCore

$(call enable-bindings,pyqt pyside pygobject)

bindings = pyqt pygobject
ifeq ($(PYTHON_MAJOR),2)
bindings += pyside
endif

.PHONY: bindings
bindings : $(bindings)
