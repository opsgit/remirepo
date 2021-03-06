%{!?__pear: %{expand: %%global __pear %{_bindir}/pear}}
%global pear_name PhpDocumentor

Summary:          The complete documentation solution for PHP
Name:             php-pear-PhpDocumentor
Version:          1.4.4
Release:          2%{?dist}
License:          LGPLv2+
Group:            Development/Libraries
URL:              http://www.phpdoc.org/
Source0:          http://pear.php.net/get/%{pear_name}-%{version}.tgz
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:        noarch
BuildRequires:    php-pear >= 1:1.4.9
# to run test suite
BuildRequires:    php-pear(pear.phpunit.de/PHPUnit) >= 3.6.0

Requires:         php-pear(PEAR)
Requires:         php-Smarty >= 2.6.0
Requires:         php-pear(XML_Beautifier) >= 1.1
Requires(post):   %{__pear}
Requires(postun): %{__pear}
Provides:         php-pear(%{pear_name}) = %{version}

Provides:         phpdoc = %{version}
Obsoletes:        phpdoc < %{version}
Provides:         php-pear-PhpDocumentor-docs = %{version}
Obsoletes:        php-pear-PhpDocumentor-docs < %{version}


%description
phpDocumentor is the current standard auto-documentation tool for the 
php language. phpDocumentor has support for linking between documentation, 
incorporating user level documents like tutorials and creation of 
highlighted source code with cross referencing to php general 
documentation.

phpDocumentor uses an extensive templating system to change your source 
code comments into human readable, and hence useful, formats. This system 
allows the creation of easy to read documentation in 15 different 
pre-designed HTML versions, PDF format, Windows Helpfile CHM format, and 
in Docbook XML. 


%prep
%setup -q -c
[ -f package2.xml ] || mv package.xml package2.xml
mv package2.xml %{pear_name}-%{version}/%{pear_name}.xml
cd %{pear_name}-%{version}

# don't install our own php-Smarty
# don't install scripts in bin, but in doc
sed -e '/Smarty-2/d' \
    -e '/name="scripts/s/role="php"/role="doc"/' \
    -i %{pear_name}.xml


%build


%install
cd %{pear_name}-%{version}
rm -rf $RPM_BUILD_ROOT
%{__pear} install --nodeps --packagingroot $RPM_BUILD_ROOT %{pear_name}.xml

# Clean up unnecessary files
rm -rf $RPM_BUILD_ROOT%{pear_phpdir}/.??*

# Install XML package description
mkdir -p $RPM_BUILD_ROOT%{pear_xmldir}
install -pm 644 %{pear_name}.xml $RPM_BUILD_ROOT%{pear_xmldir}

# Point to the system php-Smarty
sed -i -e "s|phpDocumentor/Smarty-2.6.0/libs|Smarty|" \
    $RPM_BUILD_ROOT%{pear_phpdir}/%{pear_name}/phpDocumentor/Converter.inc


%check
cd %{pear_name}-%{version}/tests

# quick hack for phpunit 3.6.0 compatibility
for i in *php
do
  sed -i -e '/PHPUnit\/Framework.php/d' $i
done

# Version 1.4.4 : OK (125 tests, 244 assertions)
%{_bindir}/phpunit \
  -d date.timezone=UTC \
  AllTests.php


%clean
rm -rf $RPM_BUILD_ROOT


%post
%{__pear} install --nodeps --soft --force --register-only \
    %{pear_xmldir}/%{pear_name}.xml >/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    %{__pear} uninstall --nodeps --ignore-errors --register-only \
        %{pear_name} >/dev/null || :
fi


%files
%defattr(-,root,root,-)
%doc %{pear_docdir}/%{pear_name}
%{pear_phpdir}/%{pear_name}
%{pear_datadir}/%{pear_name}
%{pear_testdir}/%{pear_name}
%{pear_xmldir}/%{pear_name}.xml
%{_bindir}/phpdoc


%changelog
* Thu Feb 23 2012 Remi Collet <RPMS@FamilleCollet.com> - 1.4.4-2
- run test suite during build

* Thu Feb 23 2012 Remi Collet <RPMS@FamilleCollet.com> - 1.4.4-1
- update to 1.4.4
- merge in a single package
- doc in /usr/share/doc/pear

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Feb 3 2010 Christof Damian <christof@damian.net> 1.4.3-2
- use global instead of define
- use pear download url
- add php-pear-XML-Beautifier dependency
- use pear_testdir and pear_datadir macros
- make example script in docdir non executeable

* Fri Sep 18 2009 Christof Damian <christof@damian.net> - 1.4.3-1
- Upstream 1.4.3

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Jun 30 2008 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.4.2-1
- Upstream 1.4.2.

* Fri Mar 21 2008 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.4.1-2
- Use system php-Smarty.

* Sun Feb 17 2008 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.4.1-1
- Upstream 1.4.1.

* Fri Aug 17 2007 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.4.0-1
- New major upstream release 1.4.0
- Drop explicit requirements on php -- let php-pear pull in what is necessary

* Tue Jun 12 2007 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.3.2-2
- Require parent n-v-r instead of php-pear(pear-name) in phpdoc for simplicity

* Sun Jun 10 2007 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.3.2-1
- Upstream 1.3.2
- Update the spec to the latest php-pear spec standards
- Drop obsoleted patch

* Wed Jan 17 2007 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.3.1-1
- Upstream 1.3.1
- Patch for bug with php-5.2 (http://pear.php.net/bugs/bug.php?id=9151)

* Tue Jan 02 2007 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.3.0-1
- Remove bogus scripts dir in _bindir
- Require version-release instead of just version in phpdoc

* Mon Aug 28 2006 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.3.0-0.3
- Version 1.3.0 stable
- Drop Source1
- Move documentation into -docs subpackage
- Use an updated pear template from #198706

* Sun Aug 06 2006 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.3.0-0.2.RC6
- Split command-line stuff into a phpdoc package.
- Rename the package to conform to the php-pear naming standard.
- Create a php.ini with limit overrides (builds in mock were failing)

* Thu Jul 27 2006 Konstantin Ryabitsev <icon@fedoraproject.org> - 1.3.0-0.1.RC6
- Initial packaging (merci, Remi!)
