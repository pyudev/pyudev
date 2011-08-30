include bindings/sip.mk

pyqt = PyQt-x11-gpl-4.8.5
pyqtarchive = $(pyqt).tar.gz
pyqturl = $(pyqtdownloads)/PyQt4/$(pyqt).tar.gz
havepyqt = $(call checkmodule,PyQt4.QtCore)

QMAKE := $(or $(call checkprogram,qmake),$(call checkprogram,qmake-qt4))

$(eval $(call download-rule,$(pyqturl),$(pyqt).tar.gz))
$(eval $(call builddir-rule,$(pyqt).tar.gz,$(pyqt)))

build-pyqt : sip $(call builddir,$(pyqt))
	$(call configure,$(pyqt)) --confirm-license --concatenate \
		--enable QtCore --no-designer-plugin --no-sip-files \
		--no-qsci-api --qmake $(QMAKE)
	$(call make,$(pyqt))
	$(call mk-stamp,pyqt)

$(eval $(call binding-rule,pyqt))
