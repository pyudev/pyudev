# build in temporary directory by default
DOWNLOADDIR = /tmp
BUILDDIR = /tmp

$(DOWNLOADDIR) :
	mkdir -p $(DOWNLOADDIR)

$(BUILDDIR) :
	mkdir -p $(BUILDDIR)

PYTHON = python
PYTHON_MAJOR := $(shell $(PYTHON) -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR := $(shell $(PYTHON) -c 'import sys; print(sys.version_info[1])')
PYTHON_VERSION := $(PYTHON_MAJOR).$(PYTHON_MINOR)
PYTHON_FULL = python$(PYTHON_VERSION)

PREFIX = $(shell $(PYTHON) -c 'import sys; sys.stdout.write(sys.prefix)')
LIBDIR = $(PREFIX)/lib

# some general environment variables
export LD_LIBRARY_PATH = $(LIBDIR)
export PKG_CONFIG_PATH = $(LIBDIR)/pkgconfig

checkmodule = $(shell $(PYTHON) -c 'import $(1); print("yes")')
checkprogram = $(shell which $(1))
checkpackage = $(shell PKG_CONFIG_PATH=$(PKG_CONFIG_PATH) \
	pkg-config --exists $(1) && echo yes)

define download-rule
$$(DOWNLOADDIR)/$(2) : $$(DOWNLOADDIR)
	wget -c -O $$(DOWNLOADDIR)/$(2) $(1)
endef

define builddir-rule
$$(BUILDDIR)/$(2) : $$(BUILDDIR) $$(DOWNLOADDIR)/$(1)
	tar xaf $$(DOWNLOADDIR)/$(1) -C $$(BUILDDIR)
endef

builddir = $(BUILDDIR)/$(1)

define make
	$(MAKE) -C $(BUILDDIR)/$(1)
	$(MAKE) -C $(BUILDDIR)/$(1) install
endef

define cmake
	mkdir -p $(BUILDDIR)/$(1)/build
	cd $(BUILDDIR)/$(1)/build && cmake -DBUILD_TESTS=OFF \
		-DCMAKE_INSTALL_PREFIX=$(PREFIX) \
		-DCMAKE_BUILD_TYPE=RelWithDebInfo $(2) ..
	$(call make,$(1)/build)
endef

define waf
	cd $(BUILDDIR)/$(1) && \
		$(PYTHON) waf configure --prefix $(PREFIX)
	cd $(BUILDDIR)/$(1) && $(PYTHON) waf build
	cd $(BUILDDIR)/$(1) && $(PYTHON) waf install
endef

define autotools
	cd $(BUILDDIR)/$(1) && \
		PYTHON=$(PYTHON_FULL) ./configure --prefix $(PREFIX) $(2)
	$(call make,$(1))
endef

define binding-rule
.PHONY: $(1)
$(1) : $$(if $(have$(1)),,build-$(1))
endef
