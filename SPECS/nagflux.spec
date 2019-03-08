%define debug_package %{nil}

Name:           nagflux
Version:0.4.1
Release:        1.rgm
Summary:        Distributed time-series database

Group:          Development/Other
License:        MIT
URL:            https://github.com/Griesbacher/nagflux

Source0:        %name-%version.tar.gz
Source1:        config.gcfg
Source2:        nagflux.service

ExclusiveArch: x86_64
BuildRequires: golang
BuildRequires: xmlto asciidoc

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
install -d -m 755 %{buildroot}/srv/rgm/%name-%version/var
install -d -m 770 %{buildroot}/srv/rgm/%name-%version/var/log
install -d -m 775 %{buildroot}/srv/rgm/%name-%version/var/spool
# Install Files
install -p -D -m 640 %SOURCE1 %buildroot/srv/rgm/%name-%version/
install -p -D -m 750 nagflux %buildroot/srv/rgm/%name-%version/
install -p -D -m 644 %SOURCE2 %buildroot%_unitdir/%name.service

%pre
%_sbindir/groupadd -r -f %name 2>/dev/null ||:
%_sbindir/useradd -r -g %name -G %name  -c 'InfluxDB Daemon' \
        -s /sbin/nologin  -d %_sharedstatedir/%name %name 2>/dev/null ||:

%post
%post_service %name
systemctl restart nagflux
ln -s /srv/rgm/naglux-%{version} /srv/rgm/nagflux

%preun
rm -f /srv/rgm/nagflux

%files
%_unitdir/%name.service
%dir %attr(0770, root, root) /srv/rgm/nagflux-%{version}/
%dir %attr(0770, nagios, rgm) /srv/rgm/nagflux-%{version}/var/*
/srv/rgm/%{name}-%{version}/*

%changelog
* Tue Mar 07 2019 Michael Aubertin <maubertin@fr.scc.com> - 0.4.1-1.rgm
- RGM initial release
