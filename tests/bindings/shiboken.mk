include bindings/generatorrunner.mk

shiboken = shiboken-1.0.6
shibokenurl = $(pysidedownloads)/$(shiboken).tar.bz2
haveshiboken = $(call checkpackage,shiboken)

$(eval $(call download-rule,$(shibokenurl),$(shiboken).tar.bz2))
$(eval $(call builddir-rule,$(shiboken).tar.bz2,$(shiboken)))

build-shiboken: generatorrunner $(call builddir,$(shiboken))
	$(call cmake,$(shiboken),-DPython_ADDITIONAL_VERSIONS=$(PYTHON_VERSION))

$(eval $(call binding-rule,shiboken))
