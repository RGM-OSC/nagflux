%global import_path github.com/Griesbacher/nagflux

%global __find_debuginfo_files %nil
%global _unpackaged_files_terminate_build 1

%set_verify_elf_method unresolved=no
#%brp_strip_none %_bindir/*

Name:		nagflux
Version:0.4.1
Release:	1.rgm
Summary:	Distributed time-series database

Group:		Development/Other
License:	MIT
URL:		https://github.com/Griesbacher/nagflux

Source0:	%name-%version.tar.gz

ExclusiveArch:  %go_arches
#BuildRequires: rpm-build-golang
BuildRequires: xmlto asciidoc

%description
A connector which transforms performancedata from Nagios/Icinga(2)/Naemon to InfluxDB/Elasticsearch
Nagflux collects data from the NagiosSpoolfileFolder and adds informations from Livestatus. 
This data is sent to an InfluxDB, to get displayed by Grafana. 
Therefor is the tool Histou gives you the possibility to add Templates to Grafana.

%prep
%setup -q

%build

export BUILDDIR="$PWD/.gopath"
export IMPORT_PATH="%import_path"
export GOPATH="$BUILDDIR:/usr/share/gocode/"

mkdir -vp -- "${BUILDDIR}/src/${IMPORT_PATH}"
cp -alv -- * "${BUILDDIR}/src/${IMPORT_PATH}"

cd .gopath/src/${IMPORT_PATH}

export VERSION=%{version}
export COMMIT=%commit
export BRANCH=altlinux

#go get ./...


CGO_ENABLED=0 GOGC=off go install -ldflags " -s -w \
    -X main.version=$VERSION \
    " -a -installsuffix nocgo ./...

%install
export BUILDDIR="$PWD/.gopath"
export GOPATH="/usr/share/gocode/"


BINDIR="${BINDIR:-$BUILDDIR/bin}"
GOROOT="$(go env GOROOT)"
GOPATH="${GOPATH:-$GOROOT}"

if [ -z "${IGNORE_SOURCES-}" ]; then
        mkdir -p -- "${RPM_BUILD_ROOT-}/$GOPATH"
        [ ! -d "$BUILDDIR/src" ] ||
                mv -vf -- "$BUILDDIR/src" "${RPM_BUILD_ROOT-}/$GOPATH/src"
fi

[ -n "${RPM_BINDIR-}" ] ||
        RPM_BINDIR="$(rpm --eval %_bindir)"

mkdir -p -- "${RPM_BUILD_ROOT-}/$RPM_BINDIR"
for n in "$BINDIR"/*; do
        [ ! -e "$n" ] ||
                mv -vf -- "$n" "${RPM_BUILD_ROOT-}/$RPM_BINDIR"
done


rm -rf -- %buildroot%_datadir
rm -f %buildroot%_bindir/{stress_test_server,test_client}

# Install config files
install -p -D -m 640 etc/config.sample.toml %buildroot%_sysconfdir/%name/%name.conf
# Setup directories
install -d -m 755 %buildroot%_logdir/%name
install -d -m 755 %buildroot%_sharedstatedir/%name
install -d -m 755 %{buildroot}/srv
install -d -m 755 %{buildroot}/srv/rgm
install -d -m 770 %{buildroot}/srv/rgm/nagflux-%{version}
install -d -m 770 %{buildroot}/srv/rgm/nagflux-%{version}/meta
install -d -m 770 %{buildroot}/srv/rgm/nagflux-%{version}/data
install -d -m 770 %{buildroot}/srv/rgm/nagflux-%{version}/wal
# Install pid directory
install -d -m 775 %buildroot%_runtimedir/%name
# Install logrotate
install -p -D -m 644 %SOURCE101 %buildroot%_logrotatedir/%name
# Install sysv init scripts
install -p -D -m 755 %SOURCE102 %buildroot%_initdir/%name
# Install systemd unit services
install -p -D -m 644 %SOURCE103 %buildroot%_unitdir/%name.service
install -p -D -m 644 %SOURCE104 %buildroot%_tmpfilesdir/%name.conf
# Install man files
%make_install DESTDIR=%buildroot%_prefix -C man install

%pre
%_sbindir/groupadd -r -f %name 2>/dev/null ||:
%_sbindir/useradd -r -g %name -G %name  -c 'InfluxDB Daemon' \
        -s /sbin/nologin  -d %_sharedstatedir/%name %name 2>/dev/null ||:

%post
%post_service %name
systemctl restart influxdb

%preun

%files
%_bindir/*
%_man1dir/*
%_initdir/%name
%_unitdir/%name.service
%_tmpfilesdir/%name.conf
%dir %attr(0750, root, %name) %_sysconfdir/%name
%dir %attr(0770, root, %name) /srv/rgm/influxdb-data
%dir %attr(0770, root, %name) /srv/rgm/influxdb-data/meta
%dir %attr(0770, root, %name) /srv/rgm/influxdb-data/data
%dir %attr(0770, root, %name) /srv/rgm/influxdb-data/wal
%config(noreplace) %attr(0640, root, %name) %_sysconfdir/%name/%name.conf
%config(noreplace) %_logrotatedir/%name
%dir %attr(0770, root, %name) %_logdir/%name
%dir %attr(0775, root, %name) %_runtimedir/%name
%dir %attr(0755, %name, %name) %_sharedstatedir/%name

%changelog
* Tue Mar 07 2019 Michael Aubertin <maubertin@fr.scc.com> - 0.4.1-1.rgm
- RGM initial release