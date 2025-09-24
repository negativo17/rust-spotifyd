# prevent library files from being installed
%global cargo_install_lib 0

%global crate spotifyd

Name:           rust-spotifyd
Version:        0.4.1
Release:        1%{?dist}
Summary:        Spotify daemon

License:        GPL-3.0-only
URL:            https://crates.io/crates/spotifyd
Source0:        %{crates_source}
Source1:        %{crate}-%{version}-vendor.tar.xz
Source2:        %{crate}.service
Source3:        %{crate}.xml
Source4:        %{crate}-sysusers.conf
# Automatically generated patch to strip dependencies and normalize metadata
Patch0:         %{crate}-fix-metadata-auto.diff
# https://github.com/Spotifyd/spotifyd/pull/1362
Patch2:         %{crate}-librespot-0.7.1.patch

BuildRequires:  alsa-lib-devel
BuildRequires:  cargo-rpm-macros >= 26
BuildRequires:  dbus-devel
BuildRequires:  firewalld-filesystem
BuildRequires:  openssl-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  systemd-rpm-macros

%if 0%{?rhel} == 9 || 0%{?rhel} == 10 || 0%{?fedora} == 41
%{?sysusers_requires_compat}
%endif

%global _description %{expand:
An open source Spotify client running as a UNIX daemon. Spotifyd streams music
just like the official client, but is more lightweight and supports more
platforms. Spotifyd also supports the Spotify Connect protocol which makes it
show up as a device that can be controlled from the official clients.

Spotifyd requires a Spotify Premium account. Output of the daemon is on the
Pulseaudio backend.}

%description %{_description}

%package -n %{crate}
Summary:        %{summary}
License:        GPL-3.0-or-later
# Detailed breakdown:
# (Apache-2.0 OR MIT) AND BSD-3-Clause
# 0BSD OR MIT OR Apache-2.0
# Apache-2.0
# Apache-2.0 AND ISC
# Apache-2.0 OR BSL-1.0
# Apache-2.0 OR ISC OR MIT
# Apache-2.0 OR MIT
# Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT
# BSD-2-Clause OR Apache-2.0 OR MIT
# BSD-3-Clause
# GPL-3.0-only
# ISC
# ISC AND (Apache-2.0 OR ISC)
# ISC AND (Apache-2.0 OR ISC) AND OpenSSL
# LGPL-3.0-or-later OR MPL-2.0
# MIT
# MIT AND (MIT OR Apache-2.0)
# MIT OR Apache-2.0
# MIT OR BSD-3-Clause
# MIT OR Zlib OR Apache-2.0
# MPL-2.0
# Unicode-3.0
# Unlicense OR MIT
# Zlib OR Apache-2.0 OR MIT

%description -n %{crate} %{_description}

%prep
%autosetup -n %{crate}-%{version} -p1 -a1
%cargo_prep -v vendor

%build
%cargo_build -f pulseaudio_backend,alsa_backend,dbus_mpris
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies
%{cargo_vendor_manifest}

%install
%cargo_install -f pulseaudio_backend,alsa_backend,dbus_mpris

# Default user systemd unit, with dbus/mpris enabled:
install -m 0644 -D -p contrib/%{crate}.service %{buildroot}%{_userunitdir}/%{crate}.service
# System systemd unit, with mpris disabled and running as a service user:
install -m 0644 -D -p %{SOURCE2} %{buildroot}%{_unitdir}/%{crate}.service

install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_prefix}/lib/firewalld/services/%{crate}.xml
install -m 0644 -D -p %{SOURCE4} %{buildroot}%{_sysusersdir}/%{crate}.conf

install -m 0644 -D -p contrib/%{crate}.conf %{buildroot}%{_sysconfdir}/%{crate}.conf
# Set static port to be used in firewalld configuration
sed -i -e 's/^#zeroconf_port.*/zeroconf_port = 57621/g' \
    %{buildroot}%{_sysconfdir}/%{crate}.conf

%check
%cargo_test

%if 0%{?rhel} == 10 || 0%{?fedora} == 41
%pre
%sysusers_create_compat %{SOURCE4}
%endif

%post
%systemd_post %{name}.service
%firewalld_reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files -n %{crate}
%license LICENSE
%license LICENSE.dependencies
%license cargo-vendor.txt
%doc CHANGELOG.md
%doc CONTRIBUTING.md
%doc CONTRIBUTORS.md
%doc README.md
%{_bindir}/%{crate}
%{_prefix}/lib/firewalld/services/%{crate}.xml
%{_sysconfdir}/%{crate}.conf
%{_sysusersdir}/%{crate}.conf
%{_userunitdir}/%{crate}.service
%{_unitdir}/%{crate}.service

%changelog
* Mon Sep 22 2025 Simone Caronni <negativo17@gmail.com> - 0.4.1-1
- Rework package completely.
- Use new rust packaging guidelines for vendored binaries.
- Use systemd sysuer for user creation.

* Tue Aug 29 2023 Simone Caronni <negativo17@gmail.com> - 0.3.5-2
- Enable dbus_mpris.

* Tue Aug 08 2023 Simone Caronni <negativo17@gmail.com> - 0.3.5-1
- Update to 0.3.5.
- Improve cargo RPM macro compliance.
- Momentarily disabled dbus_mpris.

* Tue Jan 07 2020 Simone Caronni <negativo17@gmail.com> - 0.2.20-1
- Update to 0.2.20.
- Enable firewall and zeroconf port.

* Sat Jul 13 2019 Simone Caronni <negativo17@gmail.com> - 0.2.11-1
- Update to 0.2.11.
- Enable DBUS keyring support.

* Tue Jul 24 2018 Simone Caronni <negativo17@gmail.com> - 0.2.2-1
- First build.
