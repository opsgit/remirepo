%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}
%{!?php_extdir: %{expand: %%global php_extdir %(php-config --extension-dir)}}

%global pecl_name rrd

Summary:      PHP Bindings for rrdtool
Name:         php-pecl-rrd
Version:      0.10.0
Release:      2%{?dist}
License:      PHP
Group:        Development/Languages
URL:          http://pecl.php.net/package/rrd

Source:       http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
Source2:      xml2changelog
# generate test file according to tests/testData/readme.txt
# http://pecl.php.net/bugs/22578
Source3:      rrd-test-makefile

# http://pecl.php.net/bugs/22576 - extension version
# http://pecl.php.net/bugs/22577 - long parameter
# http://pecl.php.net/bugs/22580 - rrdtool version check
Patch0:       rrd-build.patch

# http://pecl.php.net/bugs/22579 - tests are arch dependant
Patch1:       rrd-tests.patch

# http://pecl.php.net/bugs/22586 - RFE php-strversion
Patch2:       rrd-features.patch

BuildRoot:    %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: php-devel >= 5.3.2
BuildRequires: rrdtool
BuildRequires: rrdtool-devel >= 1.3.0
BuildRequires: php-pear

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Conflicts:    rrdtool-php
Provides:     php-pecl(%{pecl_name}) = %{version}
Requires:     php(zend-abi) = %{php_zend_api}
Requires:     php(api) = %{php_core_api}


%{?filter_setup:
%filter_provides_in %{php_extdir}/.*\.so$
%filter_setup
}


%description
Procedural and simple OO wrapper for rrdtool - data logging and graphing
system for time series data.


%prep 
%setup -c -q
%{_bindir}/php -n %{SOURCE2} package.xml | tee CHANGELOG | head -n 10

cd %{pecl_name}-%{version}
%patch0 -p1 -b .build
%patch1 -p1 -b .tests
%patch2 -p1 -b .features

cp %{SOURCE3} tests/testData/Makefile


%build
cd %{pecl_name}-%{version}
phpize
%configure

%{__make} %{?_smp_mflags}


%install
cd %{pecl_name}-%{version}
%{__rm} -rf %{buildroot}
%{__make} install INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
%{__mkdir_p} %{buildroot}%{_sysconfdir}/php.d
%{__cat} > %{buildroot}%{_sysconfdir}/php.d/%{pecl_name}.ini << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF

# Install XML package description
# use 'name' rather than 'pecl_name' to avoid conflict with pear extensions
%{__mkdir_p} %{buildroot}%{pecl_xmldir}
%{__install} -m 644 ../package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml


%check
cd %{pecl_name}-%{version}
php --no-php-ini \
    --define extension_dir=modules \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}

%{__make} -C tests/testData clean
%{__make} -C tests/testData all
%{__make} test NO_INTERACTION=1 | tee rpmtests.log

if  grep -q "FAILED TEST" rpmtests.log; then
  for t in tests/*diff; do
     echo "*** FAILED: $(basename $t .diff)"
     diff -u tests/$(basename $t .diff).exp tests/$(basename $t .diff).out || :
  done
%if 0%{?fedora} >= 14
  # tests only succeed with rrdtool 1.4.x
  exit 1
%endif
fi

%clean
%{__rm} -rf %{buildroot}


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%files
%defattr(-, root, root, -)
# http://pecl.php.net/bugs/22583 - Request for LICENSE
%doc CHANGELOG %{pecl_name}-%{version}/CREDITS
%config(noreplace) %{_sysconfdir}/php.d/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{name}.xml


%changelog
* Sat Mar 05 2011 Remi Collet <Fedora@FamilleCollet.com> 0.10.0-2
- improved patches
- implement rrd_strversion

* Fri Mar 04 2011 Remi Collet <Fedora@FamilleCollet.com> 0.10.0-1
- Version 0.10.0 (stable) - API 0.10.0 (beta)
- remove patches, merged upstream
- add links to 5 new upstream bugs

* Mon Jan 03 2011 Remi Collet <Fedora@FamilleCollet.com> 0.9.0-1
- Version 0.9.0 (beta) - API 0.9.0 (beta)
- initial RPM

