cairodownloads = http://cairographics.org/releases

ifeq ($(PYTHON_MAJOR),2)
pycairobase = py2cairo
pycairopackage = pycairo
else
pycairobase = pycairo
pycairopackage = py3cairo
endif
pycairo = $(pycairobase)-1.10.0
pycairourl = $(cairodownloads)/$(pycairo).tar.bz2
# accompy module check with a package check, because the build system of
# pygobject checks for the pkg-config package, not for the module.  So even if
# the module "cairo" is available, we may still be unable to build pygobject
# against it
havepycairo = $(and $(call checkmodule,cairo),$(call checkpackage,$(pycairopackage)))

$(eval $(call download-rule,$(pycairourl),$(pycairo).tar.bz2))
$(eval $(call builddir-rule,$(pycairo).tar.bz2,$(pycairo)))

build-pycairo: $(call builddir,$(pycairo))
	$(call waf,$(pycairo))

$(eval $(call binding-rule,pycairo))
