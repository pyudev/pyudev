pyqtdownloads = http://www.riverbankcomputing.com/static/Downloads/
sip = sip-4.12.4
sipurl = $(pyqtdownloads)/sip4/$(sip).tar.gz
havesip = $(call checkmodule,sip)

sipconfigure = cd $(BUILDDIR)/$(1) && $(PYTHON) configure.py

$(eval $(call download-rule,$(sipurl),$(sip).tar.gz))
$(eval $(call builddir-rule,$(sip).tar.gz,$(sip)))

build-sip : $(call builddir,$(sip))
	$(call sipconfigure,$(sip)) --incdir $(PREFIX)/include/sip
	$(call make,$(sip))

$(eval $(call binding-rule,sip))
