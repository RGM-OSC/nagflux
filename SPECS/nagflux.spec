%global import_path github.com/influxdata/influxdb
%global commit 4d5dda70165a34321f967f2b448114731e46b4d5

%global __find_debuginfo_files %nil
%global _unpackaged_files_terminate_build 1

%set_verify_elf_method unresolved=no
#%brp_strip_none %_bindir/*

Name:		influxdb
Version:1.7.4
Release:	1.rgm
Summary:	Distributed time-series database

Group:		Development/Other
License:	MIT
URL:		https://github.com/influxdata/influxdb

Source0:	%name-%version.tar.gz

Source101: influxdb.logrotate
Source102: influxdb.init
Source103: influxdb.service
Source104: influxdb.tmpfiles
Patch0: config.patch

ExclusiveArch:  %go_arches
#BuildRequires: rpm-build-golang
BuildRequires: xmlto asciidoc

%description
InfluxDB is an open source time series database with
no external dependencies. It's useful for recording metrics,
events, and performing analytics.

%prep
%setup -q
%patch0 -p0

%build
# Important!!!
# The %builddir/.gopath created by the hands. It contains the dependencies required for your project.
# This is necessary because the gdm cannot work with the vendor directory and always tries to update
# all dependencies from the external servers. So, we can't use Makefile to compile.
#
# $ go get -d github.com/influxdata/influxdb
# pushd src/github.com/influxdata/influxdb
# $ git checkout to %version
# $ dep ensure -vendor-only
# popd
# $ git rm -rf vendor
# $ cp -r src/github.com/influxdata/telegraf/vendor ./
# $ git add --force vendor
# $ git commit -m "update go pkgs by dep ensure -vendor-only"
# $ rm -rf $GOPATH/src/github.com/influxdata/influxdb


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
    -X main.commit=$COMMIT \
    -X main.branch=$BRANCH \
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
install -d -m 770 %{buildroot}/srv/rgm/influxdb-data
install -d -m 770 %{buildroot}/srv/rgm/influxdb-data/meta
install -d -m 770 %{buildroot}/srv/rgm/influxdb-data/data
install -d -m 770 %{buildroot}/srv/rgm/influxdb-data/wal
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
* Tue Mar 07 2019 Michael Aubertin <maubertin@fr.scc.com> - 1.7.4-1.rgm
- RGM configuration

* Wed Mar 06 2019 Michael Aubertin <maubertin@fr.scc.com> - 1.7.4-0.rgm
- Initial fork to RGM

* Wed Feb 27 2019 Alexey Shabalin <shaba@altlinux.org> 1.7.4-alt1
- 1.7.4

* Mon Jan 21 2019 Alexey Shabalin <shaba@altlinux.org> 1.6.5-alt1
- 1.6.5

* Thu Oct 11 2018 Alexey Shabalin <shaba@altlinux.org> 1.6.3-alt1
- 1.6.3

* Thu Jun 21 2018 Alexey Shabalin <shaba@altlinux.ru> 1.5.3-alt1%ubt
- 1.5.3

* Sat Apr 28 2018 Alexey Shabalin <shaba@altlinux.ru> 1.5.2-alt1%ubt
- 1.5.2

* Tue Feb 13 2018 Alexey Shabalin <shaba@altlinux.ru> 1.4.3-alt1%ubt
- 1.4.3

* Mon Oct 30 2017 Alexey Shabalin <shaba@altlinux.ru> 1.3.7-alt1%ubt
- 1.3.7

* Fri Oct 13 2017 Alexey Shabalin <shaba@altlinux.ru> 1.3.6-alt1%ubt
- 1.3.6

* Mon Aug 28 2017 Alexey Shabalin <shaba@altlinux.ru> 1.3.4-alt1%ubt
- 1.3.4

* Mon Aug 07 2017 Alexey Shabalin <shaba@altlinux.ru> 1.3.2-alt1%ubt
- 1.3.2

* Mon Jul 24 2017 Alexey Shabalin <shaba@altlinux.ru> 1.3.1-alt1
- First build for ALTLinux.

