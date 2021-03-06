%{!?__pear: %{expand: %%global __pear %{_bindir}/pear}}
%global pear_name phploc
%global channel pear.phpunit.de

Name:           php-phpunit-phploc
Version:        1.6.4
Release:        1%{?dist}
Summary:        A tool for quickly measuring the size of a PHP project

Group:          Development/Libraries
License:        BSD
URL:            http://sebastianbergmann.github.com/phploc/
Source0:        http://pear.phpunit.de/get/%{pear_name}-%{version}.tgz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  php-pear >= 1:1.9.4
BuildRequires:  php-channel(%{channel})
Requires:       php-common >= 5.2.7
Requires:       php-channel(%{channel})
Requires(post): %{__pear}
Requires(postun): %{__pear}
Requires:       php-pear(pear.phpunit.de/File_Iterator) >= 1.3.0
Requires:       php-pear(components.ez.no/ConsoleTools) >= 1.6

Provides:       php-pear(%{channel}/%{pear_name}) = %{version}


%description
phploc is a tool for quickly measuring the size of a PHP project.

The goal of phploc is not not to replace more sophisticated tools such as phpcs,
pdepend, or phpmd, but rather to provide an alternative to them when you just
need to get a quick understanding of a project's size.


%prep
%setup -q -c
[ -f package2.xml ] || mv package.xml package2.xml
%{__mv} package2.xml %{pear_name}-%{version}/%{name}.xml
cd %{pear_name}-%{version}

%build
cd %{pear_name}-%{version}
# Empty build section, most likely nothing required.


%install
cd %{pear_name}-%{version}
%{__rm} -rf $RPM_BUILD_ROOT docdir
%{__pear} install --nodeps --packagingroot $RPM_BUILD_ROOT %{name}.xml

# Clean up unnecessary files
%{__rm} -rf $RPM_BUILD_ROOT%{pear_phpdir}/.??*

# Install XML package description
%{__mkdir} -p $RPM_BUILD_ROOT%{pear_xmldir}
%{__install} -pm 644 %{name}.xml $RPM_BUILD_ROOT%{pear_xmldir}


%clean
%{__rm} -rf $RPM_BUILD_ROOT


%post
%{__pear} install --nodeps --soft --force --register-only \
    %{pear_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{__pear} uninstall --nodeps --ignore-errors --register-only \
        %{channel}/%{pear_name} >/dev/null || :
fi


%files
%defattr(-,root,root,-)
%{pear_xmldir}/%{name}.xml
%{pear_phpdir}/PHPLOC
%{_bindir}/phploc


%changelog
* Mon Nov 22 2011 Remi Collet <RPMS@FamilleCollet.com> - 1.6.4-1
- upstream 1.6.4, rebuild for remi repository

* Sun Nov 20 2011 Guillaume Kulakowski <guillaume DOT kulakowski AT fedoraproject DOT org> - 1.6.4-1
- upstream 1.6.4

* Thu Nov 03 2011 Remi Collet <RPMS@FamilleCollet.com> - 1.6.2-1
- upstream 1.6.2, rebuild for remi repository

* Tue Nov  1 2011 Christof Damian <christof@damian.net> - 1.6.2-1
- upstream 1.6.2

* Sat Feb 12 2011 Remi Collet <RPMS@FamilleCollet.com> - 1.6.1-1
- rebuild for remi repository

* Sat Feb 12 2011 Guillaume Kulakowski <guillaume DOT kulakowski AT fedoraproject DOT org> - 1.6.1-1
- upstream 1.6.1

* Fri Feb 12 2010 Remi Collet <RPMS@FamilleCollet.com> - 1.5.1-1
- rebuild for remi repository

* Wed Feb 10 2010 Christof Damian <christof@damian.net> 1.5.1-1
- upstream 1.5.1
- changed requirements
- replaced define macros with global

* Sat Jan 16 2010 Remi Collet <Fedora@FamilleCollet.com> - 1.5.0-2
- rebuild for remi repository

* Thu Jan 14 2010 Christof Damian <christof@damian.net> - 1.5.0-2
- add php 5.2.0 dependency
- remove hack to lower pear requirement

* Sun Jan  3 2010 Christof Damian <christof@damian.net> - 1.5.0-1
- upstream 1.5.0

* Fri Dec 18 2009 Guillaume Kulakowski <guillaume DOT kulakowski AT fedoraproject DOT org> - 1.4.0-2
- /usr/share/pear/PHPLOC wasn't owned

* Fri Dec 18 2009 Remi Collet <Fedora@FamilleCollet.com> - 1.4.0-1
- rebuild for remi repository

* Sat Dec 12 2009 Christof Damian <christof@damian.net> - 1.4.0-1
- upstream 1.4.0

* Wed Nov 11 2009 Remi Collet <Fedora@FamilleCollet.com> - 1.2.0-2
- rebuild for remi repository

* Sat Nov 7 2009 Guillaume Kulakowski <guillaume DOT kulakowski AT fedoraproject DOT org> - 1.2.0-2
- F-(10|11) compatibility

* Tue Oct 13 2009 Guillaume Kulakowski <guillaume DOT kulakowski AT fedoraproject DOT org> - 1.2.0-1
- Initial packaging
