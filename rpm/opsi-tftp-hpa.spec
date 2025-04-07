%if ! %{defined _fillupdir}
  %define _fillupdir /var/adm/fillup-templates
%endif

Summary: 	The client for the Trivial File Transfer Protocol (TFTP)
Name: 		opsi-tftp-hpa
Version:        5.2.9
Release:        80
License: 	AGPL-3.0-only
Group: 		Applications/Internet
#Source0: http://www.kernel.org/pub/software/network/tftp/tftp-hpa-%{version}.tar.gz
Source:         opsi-tftp-hpa_5.2.9.tar.gz
%if 0%{?rhel_version} >= 700 || 0%{?centos_version} >= 700
BuildRequires: systemd autoconf
%else
BuildRequires: tcpd-devel systemd-rpm-macros
%endif
#BuildRoot: %{_tmppath}/%{name}-root
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%if 0%{?suse_version} || 0%{?is_opensuse}
# SLES && OpenSUSE
%define opsitftpboot /var/lib/tftpboot
%else
%define opsitftpboot /tftpboot
%endif

%define toplevel_dir %{name}-%{version}

%description
The Trivial File Transfer Protocol (TFTP) is normally used only for
booting diskless workstations.  The tftp package provides the user
interface for TFTP, which allows users to transfer files to and from a
remote machine.  This program and TFTP provide very little security,
and should not be enabled unless it is expressly needed.
%package server
Group: System Environment/Daemons
Summary: The server for the Trivial File Transfer Protocol (TFTP).
Provides: opsi-tftpd
Obsoletes: opsi-atftp
Conflicts: opsi-atftp
%description server
The Trivial File Transfer Protocol (TFTP) is normally used only for
booting diskless workstations.  The tftp-server package provides the
server for TFTP, which allows users to transfer files to and from a
remote machine. TFTP provides very little security, and should not be
enabled unless it is expressly needed.  The TFTP server is run from
/etc/xinetd.d/tftp, and is disabled by default on Red Hat Linux systems.

%prep
%setup -q -n opsi-tftp-hpa-%{version}

%build
%configure
make %{?_smp_mflags}

%install 
%if 0%{?suse_version} || 0%{?is_opensuse}
  #Adjusting tftpboot directory
  sed --in-place "s_/tftpboot_/var/lib/tftpboot_" "debian/opsi-tftpd-hpa.service" || true
%endif

if [ ! -f /proc/net/if_inet6 ]; then
  # enable only ipv4 in opsi-tftpd-hpa.service file
  sed --in-place "s/-vvvvv --listen/-vvvvv --ipv4 --listen/g" "debian/opsi-tftpd-hpa.service" || true
fi
#rm -rf ${RPM_BUILD_ROOT}
install -D -m 644 debian/opsi-tftpd-hpa.service %{buildroot}%{_unitdir}/opsi-tftpd-hpa.service
mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man{1,8}
mkdir -p ${RPM_BUILD_ROOT}%{_sbindir}
mkdir -p ${RPM_BUILD_ROOT}%{opsitftpboot}
make INSTALLROOT=${RPM_BUILD_ROOT} \
    SBINDIR=%{_sbindir} MANDIR=%{_mandir} \
	install
install -d -m 0755 %{buildroot}%{opsitftpboot}

install -d %{buildroot}%{_unitdir}
install -D -m 0644 debian/opsi-tftpd-hpa.sysconfig %{buildroot}%{_fillupdir}/sysconfig.tftp
ln -sv %{_sbindir}/service %{buildroot}%{_sbindir}/rc%{name}

%pre
# This group/user is shared with atftp, so please
# keep this in sync with atftp.spec
# add group
%{_sbindir}/groupadd -r tftp 2>/dev/null || :
# add user
%{_sbindir}/useradd -c "TFTP account" -d %{opsitftpboot} -G tftp -g tftp \
  -r -s /bin/false tftp 2>/dev/null || :

%service_add_pre opsi-tftpd-hpa.service

%post server
arg0=$1
%if 0%{?rhel_version} || 0%{?centos_version}
%systemd_post opsi-tftpd-hpa.service
%else
%service_add_post opsi-tftpd-hpa.service 
%endif

systemctl=`which systemctl 2>/dev/null` || true
if [ ! -z "$systemctl" -a -x "$systemctl" ]; then
    $systemctl enable opsi-tftpd-hpa.service && echo "Enabled opsi-tftpd-hpa.service" || echo "Enabling opsi-tftpd-hpa.service failed!"

    if [ "$arg0" -eq 1 ]; then
        # Install
        $systemctl start opsi-tftpd-hpa.service || true
    else
        # Upgrade
        $systemctl restart opsi-tftpd-hpa.service || true
    fi
fi

%preun server
%if 0%{?rhel_version} || 0%{?centos_version}
%systemd_preun opsi-tftpd-hpa.service 
%else
%service_del_preun opsi-tftpd-hpa.service
%endif


%postun server
%if 0%{?rhel_version} || 0%{?centos_version}
%systemd_postun opsi-tftpd-hpa.service
%else
%service_del_postun opsi-tftpd-hpa.service
%endif

#%clean
#rm -rf ${RPM_BUILD_ROOT}
%files
%defattr(-,root,root)
#%{_unitdir}/opsi-tftpd-hpa.service
%{_bindir}/tftp
%{_mandir}/man1/*
%files server
%defattr(-,root,root)
%{_unitdir}/opsi-tftpd-hpa.service
#%dir %{opsitftpboot}
%{_sbindir}/in.tftpd
%{_sbindir}/rc%{name}
%{_mandir}/man8/*

#%dir %attr(0755,tftp,tftp) %{opsitftpboot}
%{_fillupdir}/sysconfig.tftp

# ===[ changelog ]==================================
%changelog
