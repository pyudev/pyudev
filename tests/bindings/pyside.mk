include bindings/shiboken.mk

pyside = pyside-qt4.7+1.0.6.1
pysideurl = $(pysidedownloads)/$(pyside).tar.bz2
havepyside = $(call checkmodule,PySide.QtCore)

$(eval $(call download-rule,$(pysideurl),$(pyside).tar.bz2))
$(eval $(call builddir-rule,$(pyside).tar.bz2,$(pyside)))

pyside-disabled-modules = QtGui QtMultimedia QtNetwork QtOpenGL QtScript \
	QtScriptTools QtSql QtSvg QtWebKit QtXml QtXmlPatterns QtDeclarative \
	phonon QtUiTools QtHelp QtTest

build-pyside: generatorrunner $(call builddir,$(pyside))
	$(call cmake,$(pyside), \
		-DPython_ADDITIONAL_VERSIONS=$(PYTHON_VERSION) \
		$(foreach mod,$(pyside-disabled-modules),-DDISABLE_$(mod)=ON))

$(eval $(call binding-rule,pyside))
