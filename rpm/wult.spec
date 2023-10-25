Name:     wult
Version:  1.12.13
Release:  %autorelease
Summary:  A tool for measuring C-state latency in Linux

License:  BSD-3-Clause AND GPL-2.0-only
Url:      https://intel.github.io/wult
Source0:  https://github.com/intel/wult/archive/v%{version}/%{name}-%{version}.tar.gz

# exclude backup kernel driver and duplications
Patch0:   exclude-dirs.patch

# measuring C-state latency for Intel architectures
ExclusiveArch:  x86_64

BuildRequires:  bpftool
BuildRequires:  clang
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  kernel-devel
BuildRequires:  libbpf-devel
BuildRequires:  python3-devel
BuildRequires:  python3-pytest
Requires:		pciutils
Requires:		pepc
Requires:		stats-collect
Requires:		python3-%{name} = %{version}-%{release}

%description
The name Wult comes from "Wake Up Latency Tracer". Wult measures C-state
latency by scheduling a delayed interrupt at a known time in the future, so it
relies on devices allowing for delayed interrupts. Today wult can use LAPIC as
the source of delayed interrupts, as well as I210 PCIe Gigabit Ethernet
adapter. However, other devices could be supported as well, for example other
Intel Ethernet adapters.

%package -n python3-%{name}
Summary: Wult Python library
BuildArch:  noarch

%description -n python3-%{name}
Wult Python libraries

%prep
%autosetup -p1 -n %{name}-%{version}

%generate_buildrequires
%pyproject_buildrequires -r

%build
%pyproject_wheel

%make_build -C helpers/ndl-helper
%make_build -C helpers/wult-hrt-helper
%make_build -C helpers/wult-tdt-helper

%install
%pyproject_install
%pyproject_save_files wultlibs wulttools

install -pDm755 helpers/ndl-helper/ndl-helper %{buildroot}%{_bindir}/ndl-helper
install -pDm755 helpers/wult-hrt-helper/wult-hrt-helper %{buildroot}%{_bindir}/wult-hrt-helper
install -pDm755 helpers/wult-tdt-helper/wult-tdt-helper %{buildroot}%{_bindir}/wult-tdt-helper
install -pDm644 docs/man1/exercise-sut.1 %{buildroot}/%{_mandir}/man1/exercise-sut.1
install -pDm644 docs/man1/ndl.1 %{buildroot}/%{_mandir}/man1/ndl.1
install -pDm644 docs/man1/wult.1 %{buildroot}/%{_mandir}/man1/wult.1

%check
%pytest -v

%files
%doc README.md CHANGELOG.md
%license LICENSE.md
%{_bindir}/exercise-sut
%{_bindir}/ipmi-helper
%{_bindir}/ndl
%{_bindir}/ndl-helper
%{_bindir}/stc-agent
%{_bindir}/wult
%{_bindir}/wult-hrt-helper
%{_bindir}/wult-tdt-helper
%{_datadir}/wult
%{_mandir}/man1/exercise-sut.1*
%{_mandir}/man1/ndl.1*
%{_mandir}/man1/wult.1*

%files -n python3-%{name} -f %{pyproject_files}

%changelog
%autochangelog
