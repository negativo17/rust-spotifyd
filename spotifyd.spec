%global user %{name}
%global group %{name}

Name:           spotifyd
Version:        0.2.2
Release:        1%{?dist}
Summary:        A Spotify daemon
License:        GPLv3
URL:            https://github.com/Spotifyd/spotifyd

ExclusiveArch:  %{rust_arches}

Source0:        %{url}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}.macro
Source2:        %{name}.service
Source3:        %{name}.conf

BuildRequires:  alsa-lib-devel
#BuildRequires:  firewalld-filesystem
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  rust-packaging
BuildRequires:  systemd

#Requires:       firewalld-filesystem
#Requires(post): firewalld-filesystem
Requires(pre):  shadow-utils

%description
An open source Spotify client running as a UNIX daemon. Spotifyd streams music
just like the official client, but is more lightweight and supports more
platforms. Spotifyd also supports the Spotify Connect protocol which makes it
show up as a device that can be controlled from the official clients.

Spotifyd requires a Spotify Premium account. Output of the daemon is on the
Pulseaudio backend.

%prep
%autosetup
# Override macro that points to local rust packages
%global cargo_prep %(cat %{SOURCE1})
%cargo_prep

%build
%cargo_build --features pulseaudio_backend

%install
mkdir -p %{buildroot}%{_localstatedir}/cache/%{name}

install -m 0644 -D -p %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/%{name}.conf

%cargo_install
mv %{buildroot}/%{_bindir} %{buildroot}/%{_sbindir}

%pre
getent group %{group} >/dev/null || groupadd -r %{group}
getent passwd %{user} >/dev/null || \
    useradd -r -g %{group} -d / -s /sbin/nologin \
    -c "Spotify daemon" %{user}
exit 0

%post
%systemd_post %{name}.service
#%firewalld_reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENCE
%doc README.md
%attr(640,%{user},%{group}) %{_sysconfdir}/%{name}.conf
%attr(750,%{user},%{group}) %{_localstatedir}/cache/%{name}
%{_sbindir}/%{name}
#%{_prefix}/lib/firewalld/services/%{name}.xml
%{_unitdir}/%{name}.service

%changelog
* Tue Jul 24 2018 Simone Caronni <negativo17@gmail.com> - 0.2.2-1
- First build.
