Summary: The client for the Trivial File Transfer Protocol (TFTP).
Name: tftp
Version:        5.2
Release:        8
License: BSD
Group: Applications/Internet
#Source0: http://www.kernel.org/pub/software/network/tftp/tftp-hpa-%{version}.tar.gz
Source:         tftp-hpa_5.2-8.tar.gz
BuildRequires: tcp_wrappers-devel
#BuildRoot: %{_tmppath}/%{name}-root
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

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
%setup -q -n tftp-hpa-%{version}-%{release} 
%build
%configure
make %{?_smp_mflags}
%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man{1,8}
mkdir -p ${RPM_BUILD_ROOT}%{_sbindir}
make INSTALLROOT=${RPM_BUILD_ROOT} \
    SBINDIR=%{_sbindir} MANDIR=%{_mandir} \
	install
install -m755 -d ${RPM_BUILD_ROOT}%{_sysconfdir}/xinetd.d/ ${RPM_BUILD_ROOT}/tftpboot
#install -m644 tftp-xinetd ${RPM_BUILD_ROOT}%{_sysconfdir}/xinetd.d/tftp
cat <<EOF >$RPM_BUILD_ROOT/%{_sysconfdir}/xinetd.d/tftp
service tftp
{
    disable         = no
    socket_type     = dgram
    protocol        = udp
    wait            = yes
    user            = root
    server          = %{_sbindir}/in.tftpd
    server_args     = %{tftpboot}
    per_source      = 11
    cps             = 100 2
    flags           = IPv4
}
EOF

%post server
/sbin/service xinetd reload > /dev/null 2>&1 || :
%postun server
if [ $1 = 0 ]; then
    /sbin/service xinetd reload > /dev/null 2>&1 || :
fi
%clean
rm -rf ${RPM_BUILD_ROOT}
%files
%defattr(-,root,root)
%{_bindir}/tftp
%{_mandir}/man1/*
%files server
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/xinetd.d/tftp
%dir /tftpboot
%{_sbindir}/in.tftpd
%{_mandir}/man8/*

