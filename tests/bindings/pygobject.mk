gnomedownloads = http://ftp.gnome.org/pub/GNOME/sources
pygobject = pygobject-2.26.0
pygobjecturl = $(gnomedownloads)/pygobject/2.26/$(pygobject).tar.bz2
havegobject = $(and $(call checkmodule,glib),$(call checkmodule,gobject))

$(eval $(call download-rule,$(pygobjecturl),$(pygobject).tar.bz2))
$(eval $(call builddir-rule,$(pygobject).tar.bz2,$(pygobject)))

build-pygobject: $(call builddir,$(pygobject))
	cd $(BUILDDIR)/$(pygobject) && \
		./configure --prefix $(PREFIX) \
		--disable-dependency-tracking --disable-cairo
	$(MAKE) -C $(BUILDDIR)/$(pygobject) install

$(eval $(call binding-rule,pygobject))
