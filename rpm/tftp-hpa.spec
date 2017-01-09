Summary: The client for the Trivial File Transfer Protocol (TFTP).
Name: tftp-hpa
Version:        5.2.8
Release:        3
License: BSD
Group: Applications/Internet
#Source0: http://www.kernel.org/pub/software/network/tftp/tftp-hpa-%{version}.tar.gz
Source:         tftp-hpa_5.2.8-3.tar.gz
%if 0%{?rhel_version} >= 700 || 0%{?centos_version} >= 700
BuildRequires: tcp_wrappers-devel
%else
BuildRequires: tcpd-devel
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
%description server
The Trivial File Transfer Protocol (TFTP) is normally used only for
booting diskless workstations.  The tftp-server package provides the
server for TFTP, which allows users to transfer files to and from a
remote machine. TFTP provides very little security, and should not be
enabled unless it is expressly needed.  The TFTP server is run from
/etc/xinetd.d/tftp, and is disabled by default on Red Hat Linux systems.
%prep
%setup -q -n tftp-hpa-%{version}
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
install -m644 tftp-xinetd ${RPM_BUILD_ROOT}%{_sysconfdir}/xinetd.d/tftp
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

