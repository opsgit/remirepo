%{!?phpname:		%{expand: %%global phpname     php}}

%if %{phpname} == php
%global phpbindir      %{_bindir}
%global phpconfdir     %{_sysconfdir}
%global phpincldir     %{_includedir}
%global peardir        %{_datadir}/pear
%else
%global phpbindir      %{_bindir}/%{phpname}
%global phpconfdir     %{_sysconfdir}/%{phpname}
%global phpincldir     %{_includedir}/%{phpname}
%global peardir        %{_datadir}/%{phpname}/pear
%endif


%global xmlrpcver 1.5.4
%global getoptver 1.3.0
%global arctarver 1.3.7
%global structver 1.0.4
%global xmlutil   1.2.1

Summary: PHP Extension and Application Repository framework
Name: %{phpname}-pear
Version: 1.9.1
Release: 7%{?dist}
Epoch: 1
# PEAR, Archive_Tar, XML_Util are BSD
# XML-RPC, Console_Getopt are PHP
# Structures_Graph is LGPLv2+
License: BSD and PHP and LGPLv2+
Group: Development/Languages
URL: http://pear.php.net/package/PEAR
Source0: http://download.pear.php.net/package/PEAR-%{version}.tgz
# wget http://svn.php.net/viewvc/pear/pear-core/trunk/install-pear.php?revision=287906&view=co -O install-pear.php
Source1: install-pear.php
Source2: relocate.php
Source3: strip.php
Source4: LICENSE-XML_RPC
Source10: pear.sh
Source11: pecl.sh
Source12: peardev.sh
Source13: macros.pear
Source20: http://pear.php.net/get/XML_RPC-%{xmlrpcver}.tgz
Source21: http://pear.php.net/get/Archive_Tar-%{arctarver}.tgz
Source22: http://pear.php.net/get/Console_Getopt-%{getoptver}.tgz
Source23: http://pear.php.net/get/Structures_Graph-%{structver}.tgz
Source24: http://pear.php.net/get/XML_Util-%{xmlutil}.tgz

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: %{phpname}-cli >= 5.1.0-1, %{phpname}-xml, gnupg

Provides: %{phpname}-pear(Console_Getopt) = %{getoptver}
Provides: %{phpname}-pear(Archive_Tar) = %{arctarver}
Provides: %{phpname}-pear(PEAR) = %{version}
Provides: %{phpname}-pear(Structures_Graph) = %{structver}
Provides: %{phpname}-pear(XML_RPC) = %{xmlrpcver}
Provides: %{phpname}-pear(XML_Util) = %{xmlutil}
Obsoletes: %{phpname}-pear-XML-Util <= %{xmlutil}
Provides:  %{phpname}-pear-XML-Util = %{xmlutil}-%{release}
Requires:  %{phpname}-cli >= 5.1.0-1


%description
PEAR is a framework and distribution system for reusable PHP
components.  This package contains the basic PEAR components.

%prep
%setup -cT

# Create a usable PEAR directory (used by install-pear.php)
for archive in %{SOURCE0} %{SOURCE21} %{SOURCE22} %{SOURCE23} %{SOURCE24}
do
    tar xzf  $archive --strip-components 1 || tar xzf  $archive --strip-path 1
    file=${archive##*/}
    [ -f LICENSE ] && mv LICENSE LICENSE-${file%%-*}
    [ -f README ]  && mv README  README-${file%%-*}
done
tar xzf %{SOURCE24} package.xml
mv package.xml XML_Util.xml

# apply patches on used PEAR during install
# -- no patch

%{__sed} -e "s:@BINDIR@:%{phpbindir}:;s:@PEARDIR@:%{peardir}:;s:@CONFDIR@:%{phpconfdir}:" %{SOURCE10} >pear.sh
%{__sed} -e "s:@BINDIR@:%{phpbindir}:;s:@PEARDIR@:%{peardir}:;s:@CONFDIR@:%{phpconfdir}:" %{SOURCE11} >pecl.sh
%{__sed} -e "s:@BINDIR@:%{phpbindir}:;s:@PEARDIR@:%{peardir}:;s:@CONFDIR@:%{phpconfdir}:" %{SOURCE12} >pdev.sh
%{__sed} -e "s:@BINDIR@:%{phpbindir}:;s:@PEARDIR@:%{peardir}:;s:@CONFDIR@:%{phpconfdir}:" %{SOURCE13} >macros


%build
# This is an empty build section.

%install
rm -rf $RPM_BUILD_ROOT

export PHP_PEAR_SYSCONF_DIR=%{phpconfdir}
export PHP_PEAR_SIG_KEYDIR=%{phpconfdir}/pearkeys
export PHP_PEAR_SIG_BIN=%{_bindir}/gpg
export PHP_PEAR_INSTALL_DIR=%{peardir}

# 1.4.11 tries to write to the cache directory during installation
# so it's not possible to set a sane default via the environment.
# The ${PWD} bit will be stripped via relocate.php later.
export PHP_PEAR_CACHE_DIR=${PWD}%{_localstatedir}/cache/php-pear
export PHP_PEAR_TEMP_DIR=/var/tmp

install -d $RPM_BUILD_ROOT%{peardir} \
           $RPM_BUILD_ROOT%{_localstatedir}/cache/php-pear \
           $RPM_BUILD_ROOT%{_localstatedir}/www/html \
           $RPM_BUILD_ROOT%{peardir}/.pkgxml \
           $RPM_BUILD_ROOT%{_sysconfdir}/rpm \
           $RPM_BUILD_ROOT%{phpconfdir}/pear

export INSTALL_ROOT=$RPM_BUILD_ROOT

%{phpbindir}/php -n -dmemory_limit=32M -dshort_open_tag=0 -dsafe_mode=0 \
         -derror_reporting=E_ALL -ddetect_unicode=0 \
      %{SOURCE1} -d %{peardir} \
                 -c %{phpconfdir}/pear \
                 -b %{phpbindir} \
                 -p %{phpbindir}/php \
                 -w %{_localstatedir}/www/html \
                 %{SOURCE0} %{SOURCE21} %{SOURCE22} %{SOURCE23} %{SOURCE24} %{SOURCE20}

# Replace /usr/bin/* with simple scripts:
install -m 755 pear.sh $RPM_BUILD_ROOT%{phpbindir}/pear
install -m 755 pecl.sh $RPM_BUILD_ROOT%{phpbindir}/pecl
install -m 755 pdev.sh $RPM_BUILD_ROOT%{phpbindir}/peardev

# Sanitize the pear.conf
%{phpbindir}/php -n %{SOURCE2} $RPM_BUILD_ROOT%{phpconfdir}/pear.conf $RPM_BUILD_ROOT | 
  %{phpbindir}/php -n %{SOURCE2} php://stdin $PWD > new-pear.conf
%{phpbindir}/php -n %{SOURCE3} new-pear.conf ext_dir |
  %{phpbindir}/php -n %{SOURCE3} php://stdin http_proxy > $RPM_BUILD_ROOT%{phpconfdir}/pear.conf

%{phpbindir}/php -r "print_r(unserialize(substr(file_get_contents('$RPM_BUILD_ROOT%{phpconfdir}/pear.conf'),17)));"

install -m 644 -c %{SOURCE4} LICENSE-XML_RPC

install -m 644 -c macros $RPM_BUILD_ROOT%{_sysconfdir}/rpm/macros.%{name}     

# apply patches on installed PEAR tree
pushd $RPM_BUILD_ROOT%{peardir} 
# -- no patch
popd

# Why this file here ?
rm -rf $RPM_BUILD_ROOT/.depdb* $RPM_BUILD_ROOT/.lock $RPM_BUILD_ROOT/.channels $RPM_BUILD_ROOT/.filemap

# Need for re-registrying XML_Util
install -m 644 XML_Util.xml $RPM_BUILD_ROOT%{peardir}/.pkgxml/


%check
# Check that no bogus paths are left in the configuration, or in
# the generated registry files.
grep $RPM_BUILD_ROOT $RPM_BUILD_ROOT%{phpconfdir}/pear.conf && exit 1
grep %{_libdir} $RPM_BUILD_ROOT%{phpconfdir}/pear.conf && exit 1
grep '"/tmp"' $RPM_BUILD_ROOT%{phpconfdir}/pear.conf && exit 1
grep /usr/local $RPM_BUILD_ROOT%{phpconfdir}/pear.conf && exit 1
grep -rl $RPM_BUILD_ROOT $RPM_BUILD_ROOT && exit 1


%clean
rm -rf $RPM_BUILD_ROOT
rm new-pear.conf


%triggerpostun -- %{phpname}-pear-XML-Util
# re-register extension unregistered during postun of obsoleted php-pear-XML-Util
%{phpbindir}/pear install --nodeps --soft --force --register-only %{peardir}/.pkgxml/XML_Util.xml >/dev/null || :


%files
%defattr(-,root,root,-)
%{peardir}
%{phpbindir}/*
%config(noreplace) %{phpconfdir}/pear.conf
%config %{_sysconfdir}/rpm/macros.%{name}
%dir %{_localstatedir}/cache/php-pear
%dir %{_localstatedir}/www/html
%dir %{phpconfdir}/pear
%doc README* LICENSE*


%changelog
* Mon Dec 27 2010 Remi Collet <rpms@famillecollet.com> 1:1.9.1-7
- relocate using phpname macro

* Sun Dec 12 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.1-6
- update Console_Getopt to 1.3.0
- don't require php-devel (#657812)
- update install-pear.php

* Tue Oct 26 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.1-5
- update Structures_Graph to 1.0.4

* Fri Sep 10 2010 Joe Orton <jorton@redhat.com> - 1:1.9.1-4
- ship LICENSE file for XML_RPC

* Fri Sep 10 2010 Joe Orton <jorton@redhat.com> - 1:1.9.1-3
- require php-devel (without which pecl doesn't work)

* Mon Jul 05 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.1-2
- update to XML_RPC-1.5.4

* Thu May 27 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.1-1
- update to 1.9.1

* Thu Apr 29 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.0-5
- update to Archive_Tar-1.3.7 (only metadata fix)

* Tue Mar 09 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.0-4
- update to Archive_Tar-1.3.6

* Sat Jan 16 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.0-3
- update to XML_RPC-1.5.3
- fix licenses (multiple)
- provide bundled LICENSE files

* Fri Jan 01 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.0-2
- update to Archive_Tar-1.3.5, Structures_Graph-1.0.3

* Sat Sep 05 2009 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.0-1
- update to PEAR 1.9.0, XML_RPC 1.5.2

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat May 30 2009 Remi Collet <Fedora@FamilleCollet.com> 1:1.8.1-1
- update to 1.8.1
- Update install-pear.php script (1.39)
- add XML_Util

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.7.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun May 18 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.2-2
- revert to install-pear.php script 1.31 (for cfg_dir)

* Sun May 18 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.2-1
- update to 1.7.2
- Update install-pear.php script (1.32)

* Tue Mar 11 2008 Tim Jackson <rpm@timj.co.uk> 1:1.7.1-2
- Set cfg_dir to be %%{_sysconfdir}/pear (and own it)
- Update install-pear.php script
- Add %%pear_cfgdir and %%pear_wwwdir macros

* Sun Feb  3 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.1-1
- update to 1.7.1

* Fri Feb  1 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.0-1
- update to 1.7.0

* Thu Oct  4 2007 Joe Orton <jorton@redhat.com> 1:1.6.2-2
- require php-cli not php

* Sun Sep  9 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.6.2-1
- update to 1.6.2
- remove patches merged upstream
- Fix : "pear install" hangs on non default channel (#283401)

* Tue Aug 21 2007 Joe Orton <jorton@redhat.com> 1:1.6.1-2
- fix License

* Thu Jul 19 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.6.1-1
- update to PEAR-1.6.1 and Console_Getopt-1.2.3

* Thu Jul 19 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.5.4-5
- new SPEC using install-pear.php instead of install-pear-nozlib-1.5.4.phar

* Mon Jul 16 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.5.4-4
- update macros.pear (without define)

* Mon Jul 16 2007 Joe Orton <jorton@redhat.com> 1:1.5.4-3
- add pecl_{un,}install macros to macros.pear (from Remi)

* Fri May 11 2007 Joe Orton <jorton@redhat.com> 1:1.5.4-2
- update to 1.5.4

* Tue Mar  6 2007 Joe Orton <jorton@redhat.com> 1:1.5.0-3
- add redundant build section (#226295)
- BR php-cli not php (#226295)

* Mon Feb 19 2007 Joe Orton <jorton@redhat.com> 1:1.5.0-2
- update builtin module provides (Remi Collet, #226295)
- drop patch 0

* Thu Feb 15 2007 Joe Orton <jorton@redhat.com> 1:1.5.0-1
- update to 1.5.0

* Mon Feb  5 2007 Joe Orton <jorton@redhat.com> 1:1.4.11-4
- fix Group, mark pear.conf noreplace (#226295)

* Mon Feb  5 2007 Joe Orton <jorton@redhat.com> 1:1.4.11-3
- use BuildArch not BuildArchitectures (#226925)
- fix to use preferred BuildRoot (#226925)
- strip more buildroot-relative paths from *.reg
- force correct gpg path in default pear.conf

* Thu Jan  4 2007 Joe Orton <jorton@redhat.com> 1:1.4.11-2
- update to 1.4.11

* Fri Jul 14 2006 Joe Orton <jorton@redhat.com> 1:1.4.9-4
- update to XML_RPC-1.5.0
- really package macros.pear

* Thu Jul 13 2006 Joe Orton <jorton@redhat.com> 1:1.4.9-3
- require php-cli
- add /etc/rpm/macros.pear (Christopher Stone)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1:1.4.9-2.1
- rebuild

* Mon May  8 2006 Joe Orton <jorton@redhat.com> 1:1.4.9-2
- update to 1.4.9 (thanks to Remi Collet, #183359)
- package /usr/share/pear/.pkgxml (#190252)
- update to XML_RPC-1.4.8
- bundle the v3.0 LICENSE file

* Tue Feb 28 2006 Joe Orton <jorton@redhat.com> 1:1.4.6-2
- set cache_dir directory, own /var/cache/php-pear

* Mon Jan 30 2006 Joe Orton <jorton@redhat.com> 1:1.4.6-1
- update to 1.4.6
- require php >= 5.1.0 (#178821)

* Fri Dec 30 2005 Tim Jackson <tim@timj.co.uk> 1:1.4.5-6
- Patches to fix "pear makerpm"

* Wed Dec 14 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-5
- set default sig_keydir to /etc/pearkeys
- remove ext_dir setting from /etc/pear.conf (#175673)

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Dec  6 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-4
- fix virtual provide for PEAR package (#175074)

* Sun Dec  4 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-3
- fix /usr/bin/{pecl,peardev} (#174882)

* Thu Dec  1 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-2
- add virtual provides (#173806) 

* Wed Nov 23 2005 Joe Orton <jorton@redhat.com> 1.4.5-1
- initial build (Epoch: 1 to allow upgrade from php-pear-5.x)
