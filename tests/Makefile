.PHONY: bindings

ifndef NO_BUILD
include buildbindings/bindings.mk

QT_MODULES = QtCore

$(call enable-bindings,pyqt pyside pygobject)

bindings : pyqt pyside pygobject

else
bindings :

endif
