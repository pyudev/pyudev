include bindings/apiextractor.mk

generatorrunner = generatorrunner-0.6.12
generatorrunnerurl = $(pysidedownloads)/$(generatorrunner).tar.bz2
havegeneratorrunner = $(call checkpackage,generatorrunner)

$(eval $(call download-rule,$(generatorrunnerurl),$(generatorrunner).tar.bz2))
$(eval $(call builddir-rule,$(generatorrunner).tar.bz2,$(generatorrunner)))

build-generatorrunner: apiextractor $(call builddir,$(generatorrunner))
	$(call cmake,$(generatorrunner))

$(eval $(call binding-rule,generatorrunner))
