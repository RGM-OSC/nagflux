%define debug_package %{nil}

Name:           nagflux
Version:        0.4.1
Release:        2.rgm
Summary:        Distributed time-series database

Group:          Development/Other
License:        MIT
URL:            https://github.com/Griesbacher/nagflux

Source0:        %{name}.tar.gz
Source1:        config.gcfg
Source2:        nagflux.service

ExclusiveArch: x86_64
BuildRequires: golang
BuildRequires: xmlto asciidoc
BuildRequires: rpm-macros-rgm

%description
A connector which transforms performancedata from Nagios/Icinga(2)/Naemon to InfluxDB/Elasticsearch
Nagflux collects data from the NagiosSpoolfileFolder and adds informations from Livestatus.
This data is sent to an InfluxDB, to get displayed by Grafana.
Therefor is the tool Histou gives you the possibility to add Templates to Grafana.

%prep
%setup -q

%build
go get -u github.com/griesbacher/nagflux
go build github.com/griesbacher/nagflux


%install
# Setup directories
install -d -m 0755 %{buildroot}%{rgm_path}/%name-%version/var
#install -d -m 0770 %{buildroot}%{rgm_path}/%name-%version/var/log
install -d -m 0770 %{buildroot}%{rgm_path}/%name-%version/var/spool
# Install Files
install -p -D -m 640 %SOURCE1 %buildroot%{rgm_path}/%name-%version/
install -p -D -m 750 %{name} %buildroot%{rgm_path}/%name-%version/
install -p -D -m 644 %SOURCE2 %buildroot%_unitdir/%name.service

%pre
%_sbindir/groupadd -r -f %name 2>/dev/null ||:
%_sbindir/useradd -r -g %name -G %name  -c 'InfluxDB Daemon' \
        -s /sbin/nologin  -d %_sharedstatedir/%name %name 2>/dev/null ||:

%post
%post_service %name
systemctl restart %{name}
ln -s %{rgm_path}/%{name}-%{version} %{rgm_path}/%{name}

%preun
rm -f %{rgm_path}/%{name}

%files
%_unitdir/%name.service
%dir %attr(0775, root, root) %{rgm_path}/%{name}-%{version}/
%dir %attr(0770, %{rgm_user_nagios}, %{rgm_group}) %{rgm_path}/%{name}-%{version}/var/*
%{rgm_path}/%{name}-%{version}/*

%changelog
* Thu Mar 21 2019 Eric Belhomme <ebelhomme@fr.scc.com> - 0.4.1-2.rgm
- add rpm-macros-rgm build dependency
- fix macros and typos on SPEC file
- fix systemd unit file
- fix log setup to system log defaults (/var/log/*)

* Tue Mar 07 2019 Michael Aubertin <maubertin@fr.scc.com> - 0.4.1-1.rgm
- RGM initial release
