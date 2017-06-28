Summary: The client for the Trivial File Transfer Protocol (TFTP).
Name: opsi-tftp-hpa
Version:        5.2.8
Release:        37
License: BSD
Group: Applications/Internet
#Source0: http://www.kernel.org/pub/software/network/tftp/tftp-hpa-%{version}.tar.gz
Source:         opsi-tftp-hpa_5.2.8-37.tar.gz
%if 0%{?rhel_version} >= 700 || 0%{?centos_version} >= 700
BuildRequires: tcp_wrappers-devel systemd
%else
BuildRequires: tcpd-devel systemd-rpm-macros
%endif
#BuildRoot: %{_tmppath}/%{name}-root
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

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
Requires: xinetd
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

%if 0%{?suse_version} == 1315 || 0%{?suse_version} == 1110
# SLES 12 / 11
%define tftpboot /var/lib/tftpboot
%else
%define tftpboot /tftpboot
%endif

%prep
%setup -q -n opsi-tftp-hpa-%{version}
%pre
%service_add_pre opsi-tftpd-hpa.service
%build
%configure
make %{?_smp_mflags}
%install 
%if 0%{?suse_version}
  #Adjusting tftpboot directory
  sed --in-place "s_/tftpboot_${tftpboot}_" "debian/opsi-tftpd-hpa.service" || true
%endif
#rm -rf ${RPM_BUILD_ROOT}
install -D -m 644 debian/opsi-tftpd-hpa.service %{buildroot}%{_unitdir}/opsi-tftpd-hpa.service
mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man{1,8}
mkdir -p ${RPM_BUILD_ROOT}%{_sbindir}
#mkdir -p ${RPM_BUILD_ROOT}/tftpboot
make INSTALLROOT=${RPM_BUILD_ROOT} \
    SBINDIR=%{_sbindir} MANDIR=%{_mandir} \
	install
install -m755 -d ${RPM_BUILD_ROOT}%{_sysconfdir}/xinetd.d/ ${RPM_BUILD_ROOT}/tftpboot
#install -m644 tftp-xinetd ${RPM_BUILD_ROOT}%{_sysconfdir}/xinetd.d/tftp
#cat <<EOF >$RPM_BUILD_ROOT/%{_sysconfdir}/xinetd.d/tftp
#service tftp
#{
#    disable         = no
#    socket_type     = dgram
#    protocol        = udp
#    wait            = yes
#    user            = root
#    server          = %{_sbindir}/in.tftpd
#    server_args     = -s %{tftpboot} -v -v
#    per_source      = 11
#    cps             = 100 2
#    flags           = IPv4
#}
#EOF

%post server
%if 0%{?rhel_version} || 0%{?centos_version}
%systemd_post opsi-tftpd-hpa.service
%else
%service_add_post opsi-tftpd-hpa.service
%endif

systemctl=`which systemctl 2>/dev/null` || true
if [ ! -z "$systemctl" -a -x "$systemctl" ]; then
    $systemctl enable opsi-tftpd-hpa.service && echo "Enabled opsi-tftpd-hpa.service" || echo "Enabling opsi-tftpd-hpa.service failed!"

    if [ $arg0 -eq 1 ]; then
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
#%config(noreplace) %{_sysconfdir}/xinetd.d/tftp
%{_unitdir}/opsi-tftpd-hpa.service
%dir /tftpboot
%{_sbindir}/in.tftpd
%{_mandir}/man8/*

# ===[ changelog ]==================================
%changelog
