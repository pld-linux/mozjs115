#
# Conditional build:
%bcond_without	tests	# tests build

Summary:	SpiderMonkey 115 - JavaScript implementation
Summary(pl.UTF-8):	SpiderMonkey 115 - implementacja języka JavaScript
Name:		mozjs115
Version:	115.19.0
Release:	1
License:	MPL v2.0
Group:		Libraries
#Source0:	https://download.gnome.org/teams/releng/tarballs-needing-help/mozjs/mozjs-%{version}.tar.xz
Source0:	https://ftp.mozilla.org/pub/firefox/releases/%{version}esr/source/firefox-%{version}esr.source.tar.xz
# Source0-md5:	6a14513da15bea847dd810f13d7f054d
Patch0:		copy-headers.patch
Patch1:		include-configure-script.patch
Patch2:		x32.patch
Patch3:		mozjs-x32-rust.patch
Patch4:		glibc-double.patch
Patch5:		icu76.patch
URL:		https://developer.mozilla.org/en-US/docs/Mozilla/Projects/SpiderMonkey
BuildRequires:	autoconf2_13 >= 2.13
BuildRequires:	cargo
# "TestWrappingOperations.cpp:27:1: error: non-constant condition for static assertion" with -fwrapv on gcc 6 and 7
%{?with_tests:BuildRequires:	gcc-c++ >= 6:8.1}
BuildRequires:	libicu-devel >= 73.1
BuildRequires:	libstdc++-devel >= 6:8.1
BuildRequires:	llvm
BuildRequires:	m4 >= 1.1
BuildRequires:	nspr-devel >= 4.32
BuildRequires:	perl-base >= 1:5.6
BuildRequires:	pkgconfig
BuildRequires:	python3 >= 1:3.8.5-3
BuildRequires:	python3-virtualenv >= 1.9.1-4
BuildRequires:	readline-devel
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.294
BuildRequires:	rust >= 1.66.0
BuildRequires:	rust-cbindgen >= 0.24.3
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	zlib-devel >= 1.2.3
Requires:	nspr >= 4.32
Requires:	zlib >= 1.2.3
ExclusiveArch:	%{x8664} %{ix86} x32 aarch64 armv6hl armv7hl armv7hnl
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
JavaScript Reference Implementation (codename SpiderMonkey). The
package contains JavaScript runtime (compiler, interpreter,
decompiler, garbage collector, atom manager, standard classes) and
small "shell" program that can be used interactively and with .js
files to run scripts.

%description -l pl.UTF-8
Wzorcowa implementacja JavaScriptu (o nazwie kodowej SpiderMonkey).
Pakiet zawiera środowisko uruchomieniowe (kompilator, interpreter,
dekompilator, odśmiecacz, standardowe klasy) i niewielką powłokę,
która może być używana interaktywnie lub z plikami .js do uruchamiania
skryptów.

%package devel
Summary:	Header files for JavaScript reference library
Summary(pl.UTF-8):	Pliki nagłówkowe do biblioteki JavaScript
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	libstdc++-devel >= 6:8.1
Requires:	nspr-devel >= 4.32

%description devel
Header files for JavaScript reference library.

%description devel -l pl.UTF-8
Pliki nagłówkowe do biblioteki JavaScript.

%prep
%setup -q -n firefox-%{version}
%patch -P 0 -p1
%patch -P 1 -p1
%patch -P 2 -p1
%ifarch x32
%patch -P 3 -p1
%endif
%patch -P 4 -p1
%patch -P 5 -p1

%build
export PYTHON="%{__python}"
export AUTOCONF="%{_bindir}/autoconf2_13"
export SHELL="/bin/sh"
cd js/src
%if 0
# currently rebuild not needed
AC_MACRODIR=$(pwd)/../../build/autoconf \
AWK=awk \
M4=m4 \
sh ../../build/autoconf/autoconf.sh --localdir=$(pwd) old-configure.in >old-configure
chmod 755 old-configure
%endif
mkdir -p obj
cd obj

%define configuredir ".."
%configure2_13 \
	--enable-gcgenerational \
	--disable-jemalloc \
	--enable-readline \
	--enable-shared-js \
	%{!?with_tests:--disable-tests} \
	--enable-threadsafe \
	--with-intl-api \
	--with-system-icu \
	--with-system-nspr \
	--with-system-zlib

%{__make} \
	HOST_OPTIMIZE_FLAGS= \
	MODULE_OPTIMIZE_FLAGS= \
	MOZ_OPTIMIZE_FLAGS="-freorder-blocks" \
	MOZ_PGO_OPTIMIZE_FLAGS= \
	MOZILLA_VERSION=%{version}

%install
rm -rf $RPM_BUILD_ROOT

cd js/src/obj

%{__make} -C js/src install \
	DESTDIR=$RPM_BUILD_ROOT \
	MOZILLA_VERSION=%{version}

%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.ajs

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc js/src/README.html
%attr(755,root,root) %{_bindir}/js115
%attr(755,root,root) %{_libdir}/libmozjs-115.so

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/js115-config
%{_includedir}/mozjs-115
%{_pkgconfigdir}/mozjs-115.pc
