# mock configuration:
# - Requires network for cargo dependencies

%global service_user %{name}
%global service_group %{name}

Name:           spotifyd
Version:        0.3.5
Release:        2%{?dist}
Summary:        A Spotify daemon
License:        GPLv3
URL:            https://github.com/Spotifyd/spotifyd
ExclusiveArch:  %{rust_arches}

Source0:        %{url}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

Source1:        %{name}.service
Source2:        %{name}.conf
Source3:        %{name}.xml
# Override Cargo macros
Source10:       %{name}.cargo_prep

Patch0:         https://github.com/Spotifyd/spotifyd/commit/4c944534523647ce1b7d4e485707862a86aaea56.patch

BuildRequires:  alsa-lib-devel
BuildRequires:  dbus-devel
BuildRequires:  firewalld-filesystem
BuildRequires:  gmp-devel
BuildRequires:  openssl-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  rust-packaging
BuildRequires:  systemd

Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem
Requires(pre):  shadow-utils

%description
An open source Spotify client running as a UNIX daemon. Spotifyd streams music
just like the official client, but is more lightweight and supports more
platforms. Spotifyd also supports the Spotify Connect protocol which makes it
show up as a device that can be controlled from the official clients.

Spotifyd requires a Spotify Premium account. Output of the daemon is on the
Pulseaudio backend.

%prep
%autosetup -p1

# Override macro that points to local rust packages
%global cargo_prep %(cat %{SOURCE10})
%cargo_prep

%build
%cargo_build -n -f pulseaudio_backend,dbus_keyring,dbus_mpris

%install
mkdir -p %{buildroot}%{_localstatedir}/cache/%{name}
mkdir -p %{buildroot}%{_localstatedir}/%{name}
install -m 0755 -D -p target/release/%{name} %{buildroot}/%{_sbindir}/%{name}
install -m 0644 -D -p %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
install -m 0644 -D -p %{SOURCE2} %{buildroot}%{_sysconfdir}/%{name}.conf
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

%pre
getent group %{service_group} >/dev/null || groupadd -r %{service_group}
getent passwd %{service_user} >/dev/null || \
    useradd -r -g %{service_group} -d %{_localstatedir}/%{name} -s /sbin/nologin \
    -c "Spotify daemon" %{service_user}
exit 0

%post
%systemd_post %{name}.service
#%firewalld_reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%doc CHANGELOG.md README.md
%attr(640,%{service_user},%{service_group}) %config %{_sysconfdir}/%{name}.conf
%attr(750,%{service_user},%{service_group}) %{_localstatedir}/cache/%{name}
%attr(750,%{service_user},%{service_group}) %{_localstatedir}/%{name}
%{_sbindir}/%{name}
%{_prefix}/lib/firewalld/services/%{name}.xml
%{_unitdir}/%{name}.service

%changelog
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
