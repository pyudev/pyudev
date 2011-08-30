pysidedownloads = http://www.pyside.org/files

apiextractor = apiextractor-0.10.6
apiextractorurl = $(pysidedownloads)/$(apiextractor).tar.bz2
haveapiextractor = $(call checkpackage,apiextractor)

$(eval $(call download-rule,$(apiextractorurl),$(apiextractor).tar.bz2))
$(eval $(call builddir-rule,$(apiextractor).tar.bz2,$(apiextractor)))

build-apiextractor : $(call builddir,$(apiextractor),$(haveapiextractor))
	$(call cmake,$(apiextractor))

$(eval $(call binding-rule,apiextractor))
