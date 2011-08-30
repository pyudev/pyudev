include bindings/pycairo.mk

gnomedownloads = http://ftp.gnome.org/pub/GNOME/sources
pygobject = pygobject-2.28.0
pygobjecturl = $(gnomedownloads)/pygobject/2.28/$(pygobject).tar.bz2
havegobject = $(and $(call checkmodule,glib),$(call checkmodule,gobject))

$(eval $(call download-rule,$(pygobjecturl),$(pygobject).tar.bz2))
$(eval $(call builddir-rule,$(pygobject).tar.bz2,$(pygobject)))

build-pygobject: pycairo $(call builddir,$(pygobject))
	$(call autotools,$(pygobject))

$(eval $(call binding-rule,pygobject))
