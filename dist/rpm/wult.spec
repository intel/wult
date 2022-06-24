%global debug_package %{nil}

%bcond_without tests

Name:		wult
Version:	1.10.5
Release:	1%{?dist}
Summary:	Tool for measuring Intel CPU C-state wake latency

License:	BSD-3-Clause
Url:		https://intel.github.io/wult
Source0:	https://github.com/intel/wult/archive/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:	x86_64

BuildRequires:	gcc
BuildRequires:	make
BuildRequires:	python3-devel
BuildRequires:	python3-plotly
BuildRequires:	pepc >= 1.3.8
%if %{with tests}
BuildRequires:	python3-pandas
BuildRequires:	python3-pluggy
BuildRequires:	python3-pytest
BuildRequires:	python3-numpy
BuildRequires:	python3-pyyaml
%endif
Requires:	pepc >= 1.3.8
Requires:	pciutils
Requires:	python3-pandas
Requires:	python3-plotly
Requires:	python3-numpy
Requires:	python3-pyyaml
Requires:	python3-wult
Requires:	%{name}-devel

%description
The name Wult comes from "Wake Up Latency Tracer". Wult measures C-state
latency by scheduling a delayed interrupt at a known time in the future, so it
relies on devices allowing for delayed interrupts. Today wult can use LAPIC as
the source of delayed interrupts, as well as I210 PCIe Gigabit Ethernet
adapter. However, other devices could be supported as well, for example other
Intel Ethernet adapters.

%package -n python3-%{name}
Summary:	Wult Python library
Requires:	wult

%description -n python3-%{name}
Wult Python library

%package -n %{name}-devel
Summary:        Wult Kernel drivers
Requires:	dwarves
Requires:	elfutils-libelf-devel
Requires:	wult

%description -n %{name}-devel
Wult Kernel drivers

%prep
%autosetup -p1 -n %{name}-%{version}

# pyyaml naming fix
sed -i 's/pyyml/pyyaml/g' setup.py
# pyhelpers typo
sed -i 's/pyhelpes/pyhelpers/g' wultlibs/Deploy.py

%build
%py3_build
make -C helpers/ndlrunner

%install
%py3_install
install -pDm755 helpers/ndlrunner/ndlrunner %{buildroot}%{_bindir}/ndlrunner

%check
%if %{with tests}
%pytest
%endif

%files
%doc README.md
%license debian/copyright js/dist/main.js.LICENSE.txt
%{_bindir}/ipmi-helper
%{_bindir}/ndl
%{_bindir}/ndlrunner
%{_bindir}/stats-collect
%{_bindir}/wult
%{_datadir}/wult/defs
%{_datadir}/wult/js
%exclude %{_datadir}/wult/helpers

%files -n python3-%{name}
%{python3_sitelib}/wultlibs
%{python3_sitelib}/wult-*.egg-info/

%files -n %{name}-devel
%{_datadir}/wult/drivers

# Date format: date "+%a %b %d %Y"
%changelog
* Fri Jun 24 2022 Artem Bityutskiy <artem.bityutskiy@linux.intel.com> - 1.10.6-1
- wult: add package C-states to turbostat statistics.
- wult: add current and voltage to IPMI statistics.
- Add RPM packaging support.

* Tue Jun 21 2022 Ali Erdinc Koroglu <ali.erdinc.koroglu@intel.com> - 1.10.5-1
- Initial package.
