maintainer "Sebastian Wiesner"
maintainer_email "lunaryorn@gmail.com"
license "MIT/X11"
description "Configures a virtualenv for pyudev testing"
version "0.1.0"

depends "python"
depends "apt"

recipe "pyudev", "Sets up a pyudev testing environment"
recipe "pyudev::headers", "Installs libudev headers and tools to parse these"
recipe "pyudev::bindings", "Installs native bindings supported by pyudev"
recipe "pyudev::virtualenv", "Creates a virtualenv to test pyudev"
